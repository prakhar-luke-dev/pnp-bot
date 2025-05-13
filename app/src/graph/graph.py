from langfuse.decorators import observe
import json
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, START

from config.app_config import Config
from config.log_configs import app_logger
from psycopg import Connection, OperationalError


def build_graph():
    builder = StateGraph(state_schema=AresState)

    # Add nodes
    # builder.add_node("fetch_history", fetch_user_history_node)


    # Add edges
    # builder.add_edge(START, "fetch_history")
    # builder.add_conditional_edges("decompose_question", scope_router, {False:"out_scope", True: "supervisor"})


    if Config.POSTGRES_URI:
        try :
            pool = Connection.connect(Config.POSTGRES_URI, **Config.MEMORY_CONNECTION_KWARGS)
            checkpointer = PostgresSaver(pool)
            # Only one time
            # checkpointer.setup()
        except OperationalError as e:
            raise ConnectionError(f"Failed to connect to PostgreSQL: {str(e)}")
        except ValueError as e:
            raise ValueError(f"Invalid PostgreSQL URI: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error while connecting to PostgreSQL: {str(e)}")
    else:
        app_logger.warning("POSTGRES not available using RAM for chat history (this won't be stored)")
        checkpointer = MemorySaver()

    graph = builder.compile(checkpointer=checkpointer)
    return graph

def run_graph(user_query: str, user_config: dict, somevalue1 : int):
    graph = build_graph()

    ares_reply = graph.invoke(
        {
            "messages": [("user", user_query)],
            "other_key1" : somevalue1,
        },
        config=user_config
    )
    return ares_reply

def stream_thinking_graph(user_query: str, user_config: dict, somevalue1: int):
    graph = build_graph()
    inputs = {
        "messages": [("user", user_query)],
        "other_key1": somevalue1,
    }

    for mode, chunk in graph.stream(inputs, config=user_config, stream_mode=["custom", "messages"]):
        # print(f"mode : {mode}\nchunk : {chunk}")
        data = chunk
        if mode == 'messages':
            metadata = chunk[1]
            langgraph_node = metadata["langgraph_node"]
            if langgraph_node == "combine":
                data = chunk[0].content
            else:
                continue
            yield f"ans : {data}\n"
        elif mode == "custom":
            yield f"thinking_process : {data['thinking']}\n"
        # print("MODE : ", mode, end="\n")
        # print(data, flush=True)
        # yield f"data: {data}\n\n"  # for SSE (can also use `yield json.dumps(chunk) + "\n"`)
        # yield f"data: {json.dumps(chunk)}\n\n"


def stream_graph_no_thinking(user_query: str, user_config: dict, somevalue1: int,):
    graph = build_graph()
    inputs = {
        "messages": [("user", user_query)],
        "other_key1": somevalue1,
    }
    for message_chunk, metadata in graph.stream(inputs, config=user_config, stream_mode="messages"):
        yield f"data: {message_chunk.content}\n\n"

def save_graph_png():
    file_path = "app_vida/assets/img/ares5"
    graph = build_graph()
    save_graph_to_file(runnable_graph=graph, output_file_path=file_path)
