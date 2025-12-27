"""FastAPI service for exposing agent capabilities."""
import logging
import asyncio
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
import json
import uuid

from agent import agent
from memory.conversation_manager import conversation_manager
from config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s -  %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Clinical Trial Agent API",
    description="LangChain-powered conversational agent for clinical trial queries",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class QueryRequest(BaseModel):
    """Request model for queries."""
    query: str
    session_id: str = None


class QueryResponse(BaseModel):
    """Response model for queries."""
    response: str
    session_id: str
    thinking_steps: List[Dict[str, Any]] = []


class SessionResponse(BaseModel):
    """Response model for session information."""
    session_id: str
    message_count: int


# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup."""
    logger.info("Starting Clinical Trial Agent API...")
    await agent.initialize()
    logger.info("Agent initialized and ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down...")
    await agent.shutdown()


# Endpoints
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "clinical-trial-agent",
        "version": "1.0.0"
    }


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest) -> QueryResponse:
    """
    Process a user query and return a response.
    
    Args:
        request: Query request with message and optional session ID
        
    Returns:
        Agent response with session ID
    """
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    logger.info(f"Processing query for session {session_id}")
    
    try:
        # Process query with agent
        response, thinking_steps = await agent.query(
            user_message=request.query,
            session_id=session_id
        )
        
        return QueryResponse(
            response=response,
            session_id=session_id,
            thinking_steps=thinking_steps
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stream/{session_id}")
async def stream_query(session_id: str, query: str):
    """
    Stream agent responses via Server-Sent Events.
    
    Args:
        session_id: Session identifier
        query: User query
        
    Returns:
        SSE stream of agent events
    """
    async def event_generator():
        """Generate SSE events from agent stream."""
        try:
            async for event in agent.stream_query(
               user_message=query,
                session_id=session_id
            ):
                yield {
                    "event": event["type"],
                    "data": json.dumps(event["data"])
                }
                
                # Small delay to prevent overwhelming the client
                await asyncio.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Error in stream: {str(e)}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
    
    return EventSourceResponse(event_generator())


@app.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> SessionResponse:
    """
    Get information about a conversation session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session information
    """
    messages = conversation_manager.get_messages(session_id)
    
    return SessionResponse(
        session_id=session_id,
        message_count=len(messages)
    )


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> Dict[str, str]:
    """
    Clear a conversation session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Confirmation message
    """
    conversation_manager.delete_session(session_id)
    
    return {"message": f"Session {session_id} deleted"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.agent_api_host,
        port=settings.agent_api_port,
        log_level=settings.log_level.lower()
    )
