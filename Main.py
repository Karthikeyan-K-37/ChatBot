# Main.py
import os
import openai
from dotenv import load_dotenv
from typing import Annotated
from langchain_core.messages import AIMessage, ToolMessage
from pydantic import BaseModel
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class State(TypedDict):
    messages: Annotated[list, add_messages]
    ask_human: bool

class RequestAssistance(BaseModel):
    request: str

llm = openai.ChatCompletion

def chatbot(state: State):
    user_message = state["messages"][-1]["content"] if state["messages"] else ""  
    state["messages"].append({"role": "user", "content": user_message})  

    response = llm.create(
        model="gpt-3.5-turbo",
        messages=state["messages"]
    )

    response_message = response['choices'][0]['message']
    
    ask_human = False
    if (
        response_message.get('tool_calls') and 
        response_message['tool_calls'][0]["name"] == RequestAssistance.__name__
    ):
        ask_human = True
    return {"messages": [response_message], "ask_human": ask_human}

graph_builder = StateGraph(State)

def my_tool(input_data):
    return f"Processed: {input_data}"

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=[my_tool]))

def create_response(response: str, ai_message: AIMessage):
    return ToolMessage(
        content=response,
        tool_call_id=ai_message.tool_calls[0]["id"],
    )

def human_node(state: State):
    new_messages = []
    if not isinstance(state["messages"][-1], ToolMessage):
        new_messages.append(create_response("No response from human.", state["messages"][-1]))
    return {"messages": new_messages, "ask_human": False}

graph_builder.add_node("human", human_node)

def select_next_node(state: State):
    if state["ask_human"]:
        return "human"
    return tools_condition(state)

graph_builder.add_conditional_edges(
    "chatbot",
    select_next_node,
    {"human": "human", "tools": "tools", "__end__": "__end__"},
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("human", "chatbot")
graph_builder.set_entry_point("chatbot")

memory = MemorySaver()
graph = graph_builder.compile(
    checkpointer=memory,
    interrupt_before=["human"],
)

state = {"messages": [], "ask_human": False}

def process_message(user_input: str, state: State):
    state["messages"].append({"role": "user", "content": user_input})
    return chatbot(state)
