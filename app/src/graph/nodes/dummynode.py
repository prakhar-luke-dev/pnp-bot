from typing import Literal

from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from langgraph.graph import END
from langgraph.types import Command, StreamWriter
from src.graph.states.globalstate import State
# @observe
def sample_node(state: State, writer: StreamWriter) -> Command[Literal["should_summarize", "custom_error"]]:  # NOSONAR
    """
    it's description
    Args:
        state: GraphState
        write: custom display while stream output
    """
    try:
        writer({
            "thinking": "Performing actions."
        })
        goto_node = "sample_node2"
        reset_state = {
                "next_node": "sample_node2",

                "error_in_node" : "",
                "error_message" : None,

                "llm_response": "",
            }
        return Command(
            update=reset_state,
            goto=goto_node,
        )
    except Exception as E:
        return Command(
            update={
                "error_in_node": "sample_node",
                "error_message": str(E)
            },
            goto="custom_error"
        )
