import os
import json
import uuid
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import aiomysql
import boto3
from botocore.exceptions import ClientError
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database pool global variable
db_pool = None

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_pool
    db_pool = await create_db_pool()
    await initialize_database()
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    if db_pool:
        db_pool.close()
        await db_pool.wait_closed()
    logger.info("Application shut down successfully")

# Initialize FastAPI app
app = FastAPI(
    title="Chatbot API",
    description="FastAPI backend for chatbot with AWS Bedrock and MySQL",
    version="1.0.0",
    lifespan=lifespan
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation continuity")

class ChatResponse(BaseModel):
    response: str
    session_id: str

# Environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'db': os.getenv('DB_NAME', 'chatbot_db'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'autocommit': True,
}

AWS_REGION = os.getenv('AWS_REGION', 'us-east-2')
BEDROCK_MODEL_ID = "deepseek.v3-v1:0"

# Database functions
async def create_db_pool():
    """Create MySQL connection pool with SSL/TLS encryption"""
    try:
        pool = await aiomysql.create_pool(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            db=DB_CONFIG['db'],
            autocommit=DB_CONFIG['autocommit'],
            minsize=1,
            maxsize=10
        )
        logger.info("Database pool created successfully with SSL/TLS")
        return pool
    except Exception as e:
        logger.error(f"Failed to create database pool: {str(e)}")
        raise

async def initialize_database():
    """Initialize database schema"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS conversations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        session_id VARCHAR(36) NOT NULL,
        user_message TEXT NOT NULL,
        ai_response TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_session_id (session_id),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(create_table_query)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

async def save_conversation(session_id: str, user_message: str, ai_response: str):
    """Save conversation to database"""
    insert_query = """
    INSERT INTO conversations (session_id, user_message, ai_response)
    VALUES (%s, %s, %s)
    """
    
    try:
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(insert_query, (session_id, user_message, ai_response))
        logger.info(f"Conversation saved for session: {session_id}")
    except Exception as e:
        logger.error(f"Failed to save conversation: {str(e)}")
        raise

async def get_conversation_history(session_id: str, limit: int = 10):
    """Retrieve conversation history for context"""
    select_query = """
    SELECT user_message, ai_response, created_at
    FROM conversations
    WHERE session_id = %s
    ORDER BY created_at DESC
    LIMIT %s
    """
    
    try:
        async with db_pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(select_query, (session_id, limit))
                result = await cur.fetchall()
                return list(reversed(result))  # Return in chronological order
    except Exception as e:
        logger.error(f"Failed to retrieve conversation history: {str(e)}")
        return []

# AWS Bedrock functions
def get_bedrock_client():
    """Initialize AWS Bedrock client"""
    try:
        client = boto3.client(
            service_name='bedrock-runtime',
            region_name=AWS_REGION
        )
        return client
    except Exception as e:
        logger.error(f"Failed to create Bedrock client: {str(e)}")
        raise

async def call_deepseek(message: str, conversation_history: list = None) -> str:
    """Call AWS Bedrock DeepSeek V3.1 model"""
    try:
        bedrock_client = get_bedrock_client()
        
        # Build conversation context
        messages = []
        
        # Add conversation history if available
        if conversation_history:
            for entry in conversation_history[-5:]:  # Last 5 exchanges for context
                messages.append({
                    "role": "user",
                    "content": entry['user_message']
                })
                messages.append({
                    "role": "assistant",
                    "content": entry['ai_response']
                })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        # Prepare request body for DeepSeek
        request_body = {
            "messages": messages,
            "max_tokens": 2048,
            "temperature": 0.7,
            "top_p": 0.9,
        }
        
        # Call Bedrock
        response = bedrock_client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(request_body)
        )
        
        # Parse response for DeepSeek
        response_body = json.loads(response['body'].read())
        # DeepSeek uses OpenAI-compatible format
        ai_response = response_body['choices'][0]['message']['content']
        
        logger.info("Successfully received response from DeepSeek V3.1")
        return ai_response
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"AWS Bedrock error ({error_code}): {error_message}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {error_message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error calling Bedrock: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get AI response"
        )

# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Chatbot API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Check database connection
    try:
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                await cur.fetchone()
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("5/minute")  # 5 requests per minute per IP address
async def chat(request: ChatRequest):
    """
    Chat endpoint that processes user messages and returns AI responses
    """
    try:
        # Generate or use existing session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get conversation history for context
        conversation_history = await get_conversation_history(session_id)
        
        # Call DeepSeek
        ai_response = await call_deepseek(
            message=request.message,
            conversation_history=conversation_history
        )
        
        # Save conversation to database
        await save_conversation(
            session_id=session_id,
            user_message=request.message,
            ai_response=ai_response
        )
        
        return ChatResponse(
            response=ai_response,
            session_id=session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )

@app.delete("/chat/session/{session_id}")
async def delete_session(session_id: str):
    """Delete conversation history for a session"""
    try:
        delete_query = "DELETE FROM conversations WHERE session_id = %s"
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(delete_query, (session_id,))
                affected_rows = cur.rowcount
        
        if affected_rows == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return {"message": f"Session {session_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )