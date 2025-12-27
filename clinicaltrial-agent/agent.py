"""Main agent implementation using LangGraph ReAct pattern and MCP tools."""
import logging
import contextlib
from typing import Dict, Any, List, Optional, AsyncIterator, Tuple
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from langchain_mcp_adapters.tools import load_mcp_tools
from llm.gemini_client import gemini_llm
from callbacks.progress_callback import ProgressCallback
from memory.conversation_manager import conversation_manager
from config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are TrialTalk, an advanced Clinical Trial AI Assistant. 
Your goal is to help users find, understand, and analyze clinical trials from ClinicalTrials.gov.

Guidelines:
1. Use the provided tools to search for trials based on user criteria (condition, location, phase, etc.).
2. When presenting trials, include the NCT ID, Title, Status, and Phase.
3. CITATIONS: Always cite trials you mention using their NCT ID in brackets, e.g., [NCT01234567].
4. REFERENCES SECTION: At the end of every message that discusses specific trials, include a "### References" section listing the NCT IDs and their direct ClinicalTrials.gov links (https://clinicaltrials.gov/study/[NCT_ID]).
5. If a user asks about a specific trial (by NCT ID), use the retrieve tools to get detailed information.
   - Note: For eligibility/inclusion criteria, use the field path: `protocolSection.eligibilityModule.eligibilityCriteria` (NOT inclusionCriteria).
6. Explain medical terms simply but accurately.
7. Always clarify that you are an AI assistant and not a medical professional.
8. If no trials are found, suggest broadening the search criteria.
9. Be concise but thorough in your analysis.
"""

class ClinicalTrialAgent:
    """Main conversational agent for clinical trial queries."""
    
    def __init__(self):
        """Initialize the agent."""
        self.llm = gemini_llm
        self.tools = []
        self.agent_executor = None
        self._initialized = False
        self._exit_stack = contextlib.AsyncExitStack()
    
    async def initialize(self):
        """Initialize the agent by connecting to MCP server and loading tools."""
        if self._initialized:
            return
        
        logger.info("Initializing Clinical Trial Agent with MCP tools...")
        
        try:
            # 1. Open Streamable HTTP connection
            mcp_url = settings.mcp_server_url
            if not mcp_url.endswith("/mcp"):
                mcp_url = f"{mcp_url.rstrip('/')}/mcp"
            
            logger.info(f"Connecting to MCP at: {mcp_url}")
            
            # Use the context manager - it yields 3 values: read_stream, write_stream, and session_metadata (optional)
            read_stream, write_stream, _ = await self._exit_stack.enter_async_context(
                streamable_http_client(mcp_url)
            )
            
            # 2. Create and initialize MCP session
            session = await self._exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            await session.initialize()
            
            # 3. Load tools using LangChain MCP adapter
            self.tools = await load_mcp_tools(session)
            logger.info(f"Successfully loaded {len(self.tools)} tools from MCP server")
            
            # 4. Create ReAct agent with LangGraph and System Prompt
            self.agent_executor = create_react_agent(
                self.llm,
                self.tools,
                prompt=SYSTEM_PROMPT
            )
            
            self._initialized = True
            logger.info("Agent initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {str(e)}")
            await self._exit_stack.aclose()
            raise
    
    async def query(
        self,
        user_message: str,
        session_id: str,
        event_handler=None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Process a user query and return a response along with thinking steps.
        
        Returns:
            Tuple of (final_response_string, list_of_thinking_events)
        """
        if not self._initialized:
            await self.initialize()
        
        logger.info(f"Processing query for session {session_id}: {user_message[:50]}...")
        conversation_manager.add_user_message(session_id, user_message)
        messages = conversation_manager.get_messages(session_id)
        
        # Create callback to capture events
        callback = ProgressCallback(event_handler=event_handler)
        
        try:
            result = await self.agent_executor.ainvoke(
                {"messages": messages},
                config={"callbacks": [callback]}
            )
            
            # Extract content correctly from Message object
            last_msg = result["messages"][-1]
            if isinstance(last_msg.content, list):
                response = "".join(part.get("text", "") for part in last_msg.content if isinstance(part, dict) and "text" in part)
            else:
                response = str(last_msg.content)
            
            conversation_manager.add_ai_message(session_id, response)
            
            # Filter callback events to provide "thinking" steps
            thinking_steps = [
                e for e in callback.events 
                if e["type"] in ["tool_start", "agent_action"]
            ]
            
            return response, thinking_steps
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return f"I encountered an error: {str(e)}", []
    
    async def stream_query(
        self,
        user_message: str,
        session_id: str,
        event_handler=None
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream agent responses in real-time."""
        if not self._initialized:
            await self.initialize()
        
        conversation_manager.add_user_message(session_id, user_message)
        messages = conversation_manager.get_messages(session_id)
        callback = ProgressCallback(event_handler=event_handler)
        
        try:
            async for event in self.agent_executor.astream(
                {"messages": messages},
                config={"callbacks": [callback]},
                stream_mode="values"
            ):
                if event.get("messages"):
                    yield {
                        "type": "agent_event",
                        "data": {
                            "messages": len(event["messages"]),
                            "last_message": event["messages"][-1].content
                        }
                    }
            
            # Get final response for history
            final_state = await self.agent_executor.aget_state(config={"callbacks": [callback]})
            if final_state.values.get("messages"):
                last_msg = final_state.values["messages"][-1]
                if isinstance(last_msg.content, list):
                    response = "".join(part.get("text", "") for part in last_msg.content if isinstance(part, dict) and "text" in part)
                else:
                    response = str(last_msg.content)
                    
                conversation_manager.add_ai_message(session_id, response)
                yield {
                    "type": "final_response",
                    "data": {"response": response}
                }
                
        except Exception as e:
            logger.error(f"Error streaming query: {str(e)}")
            yield {"type": "error", "data": {"error": str(e)}}
    
    async def shutdown(self):
        """Cleanup resources."""
        await self._exit_stack.aclose()
        logger.info("Agent shutdown complete")

# Global agent instance
agent = ClinicalTrialAgent()
