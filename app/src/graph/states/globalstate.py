from operator import add
from typing import Annotated
 
from langgraph.graph import MessagesState
 
 
class State(MessagesState):  # noqa
    """
    State class for Ares workflow.
 
    Extends MessagesState to track conversation history and maintains the last message received.
 
    Attributes:
        other_key1 (int) : Some key

        next_node (str) : The next node bot should refer to.
        node_path (list) : list of path taken by the graph (not in use as of now)
        
        error_in_node (list) : list of nodes with the errors
        error_message (str | None) : Error message passed from node

        llm_response (str) : Response from the language model.
    """
    
    other_key1: int
 
    next_node : str
    node_path: Annotated[list[str], add]

    error_in_node : str
    error_message : str | None

    llm_response : str

    

