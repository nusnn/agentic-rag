from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition
from dotenv import load_dotenv
import os
from tools import guest_info_tool, search_tool, weather_info_tool, get_hub_stats
env = load_dotenv()
# print("Environment variables loaded:", env)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

from langchain_openai import ChatOpenAI

# Replace HuggingFace setup with OpenAI
chat = ChatOpenAI(
    model="gpt-4o",
    openai_api_key=OPENAI_API_KEY,
    verbose=True
)

tools = [guest_info_tool, search_tool, weather_info_tool, get_hub_stats]
# tools = []

chat_with_tools = chat.bind_tools(tools)

# from langchain.agents import create_react_agent
# agent = create_react_agent(chat, tools=tools)
# Generate the AgentState and Agent graph
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

def assistant(state: AgentState):
    return {
        "messages": [chat_with_tools.invoke(state["messages"])],
        # "messages": [agent.invoke(state["messages"])],
    }

## The graph
builder = StateGraph(AgentState)

# Define nodes: these do the work
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define edges: these determine how the control flow moves
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message requires a tool, route to tools
    # Otherwise, provide a direct response
    tools_condition,
)
builder.add_edge("tools", "assistant")
alfred = builder.compile()


# content = "Alfred, who is that gentleman talking to the ambassador?"
# messages = [HumanMessage(content=content)]
# response = alfred.invoke({"messages": messages})

# print("🎩 Alfred's Response:")
# print(response['messages'][-1].content)


# messages = [HumanMessage(content="Who is Facebook and what's their most popular model?")]
# response = alfred.invoke({"messages": messages})

# print("🎩 Alfred's Response:")
# print(response['messages'][-1].content)

# response = alfred.invoke({"messages": [HumanMessage(content="Tell me about 'Lady Ada Lovelace'")]})
# for message in response["messages"]:
#     print(type(message).__name__, ":", message)
# print("🎩 Alfred's Response:")
# print(response['messages'])
# print(response['messages'][-1].content)


# response = alfred.invoke({"messages": "What's the weather like in Paris tonight? Will it be suitable for our fireworks display?"})

# print("🎩 Alfred's Response:")
# print(response['messages'][-1].content)


# response = alfred.invoke({"messages": "One of our guests is from Qwen. What can you tell me about their most popular model?"})

# print("🎩 Alfred's Response:")
# print(response['messages'][-1].content)

# response = alfred.invoke({"messages":"I need to speak with 'Dr. Nikola Tesla' about recent advancements in wireless energy. Can you help me prepare for this conversation?"})

# print("🎩 Alfred's Response:")
# print(response['messages'][-1].content)


# First interaction
response = alfred.invoke({"messages": [HumanMessage(content="Tell me about 'Lady Ada Lovelace'. What's her background and how is she related to me?")]})


print("🎩 Alfred's Response:")
print(response['messages'][-1].content)
print()

# Second interaction (referencing the first)
response = alfred.invoke({"messages": response["messages"] + [HumanMessage(content="What projects is she currently working on?")]})

print("🎩 Alfred's Response:")
print(response['messages'][-1].content)