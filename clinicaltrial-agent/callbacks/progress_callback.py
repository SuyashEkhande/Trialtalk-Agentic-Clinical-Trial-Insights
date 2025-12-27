"""Progress tracking callback for LangChain agent."""
import logging
from typing import Any, Dict, List, Optional
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import ToolMessage

logger = logging.getLogger(__name__)


class ProgressCallback(BaseCallbackHandler):
    """Callback handler for tracking agent progress and emitting events."""
    
    def __init__(self, event_handler=None):
        """
        Initialize the progress callback.
        
        Args:
            event_handler: Optional function to handle emitted events
        """
        self.event_handler = event_handler
        self.events = []
    
    def emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit an event to the event handler."""
        event = {
            "type": event_type,
            "data": data
        }
        self.events.append(event)
        
        if self.event_handler:
            self.event_handler(event)
        
        logger.debug(f"Event emitted: {event_type}")
    
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        name = serialized.get("name") if serialized else "unknown"
        self.emit_event("llm_start", {
            "prompts": prompts,
            "model": name
        })
    
    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token."""
        self.emit_event("llm_token", {"token": token})
    
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        self.emit_event("llm_end", {
            "generations": len(response.generations)
        })
    
    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Run when LLM errors."""
        self.emit_event("llm_error", {"error": str(error)})
    
    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: Any, **kwargs: Any
    ) -> None:
        """Run when tool starts running."""
        name = serialized.get("name") if serialized else "unknown"
        
        # Clean up input_str if it's a dict containing internal LangGraph context
        display_input = input_str
        if isinstance(input_str, dict):
            # Remove high-noise internal keys
            clean_input = {
                k: v for k, v in input_str.items() 
                if k not in ["runtime", "config", "callbacks", "store", "remaining_steps"]
            }
            display_input = str(clean_input)
            
        self.emit_event("tool_start", {
            "tool": name,
            "input": display_input
        })
    
    def on_tool_end(self, output: Any, **kwargs: Any) -> None:
        """Run when tool ends running."""
        # Output could be a string or a ToolMessage
        if isinstance(output, ToolMessage):
            output_str = output.content
        else:
            output_str = str(output)
            
        self.emit_event("tool_end", {"output": output_str[:200]})  # Truncate long outputs
    
    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        """Run when tool errors."""
        self.emit_event("tool_error", {"error": str(error)})
    
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        """Run on agent action."""
        self.emit_event("agent_action", {
            "tool": action.tool,
            "tool_input": str(action.tool_input)[:200],
            "log": action.log[:200] if action.log else ""
        })
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Run on agent finish."""
        self.emit_event("agent_finish", {
            "output": str(finish.return_values)[:200]
        })
    
    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Run when chain starts running."""
        name = serialized.get("name") if serialized else "unknown"
        self.emit_event("chain_start", {
            "chain": name
        })
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Run when chain ends running."""
        self.emit_event("chain_end", {})
    
    def on_chain_error(self, error: Exception, **kwargs: Any) -> None:
        """Run when chain errors."""
        self.emit_event("chain_error", {"error": str(error)})
