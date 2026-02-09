from typing import Annotated, TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from mem0 import MemoryClient
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# from helper import add_memory, search_memory
from prompts import system_prompt_template

from agent_sdk import main_agent, Runner
import asyncio

import logging

import os
from dotenv import load_dotenv

load_dotenv()

from logger import logger
logger.setLevel(logging.INFO)

client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))

class ChatbotState(TypedDict):
    memory: Dict[str, Any]
    mem0_user_id: str
    mem0_session_id: str
    context: str

    signed_in: bool
    image_data: str | None
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]


# def get_memories(state: ChatbotState):
#     messages = state["messages"]
#     user_id = state["mem0_user_id"]
#     session_id = state["mem0_session_id"]

#     logger.info(f"User ID: {user_id}")
#     logger.info(f"Session ID: {session_id}")
#     logger.info(f"Signed In: {state['signed_in']}")
    
#     if state["signed_in"]:
#         logger.info("Getting Session and Global Memories")
#         try:
#             session_based_memories = client.search(messages[-1].content, user_id=user_id, session_id=session_id) 
#             global_memories = client.search(messages[-1].content, user_id=user_id)
#         except Exception as e:
#             logger.error(f"Error fetching memories: {e}")
#             session_based_memories = {'results': []}
#             global_memories = {'results': []}
#     else:
#         logger.info("Getting Session Memories only")
#         try:
#             session_based_memories = client.search(messages[-1].content, user_id=user_id, session_id=session_id)
#         except Exception as e:
#             logger.error(f"Error fetching memories: {e}")
#             session_based_memories = {'results': []}

async def get_memories(state: ChatbotState):
    messages = state["messages"]
    user_id = state["mem0_user_id"]
    run_id = state["mem0_session_id"]  # Use as run_id instead

    logger.info(f"User ID: {user_id}")
    logger.info(f"Run ID: {run_id}")
    logger.info(f"Signed In: {state['signed_in']}")
    
    if state["signed_in"]:
        logger.info("Getting Session and Global Memories")
        try:
            # Session-based memories using run_id
            session_based_memories = client.search(
                messages[-1].content, 
                filters={"AND": [{"user_id": user_id}, {"run_id": run_id}]}
            )
            # Global memories for user
            global_memories = client.search(
                messages[-1].content, 
                filters={"user_id": user_id}
            )
        except Exception as e:
            logger.error(f"Error fetching memories: {e}")
            session_based_memories = {'results': []}
            global_memories = {'results': []}
    else:
        logger.info("Getting Session Memories only")
        try:
            session_based_memories = client.search(
                messages[-1].content, 
                filters={"AND": [{"user_id": user_id}, {"run_id": run_id}]}
            )
        except Exception as e:
            logger.error(f"Error fetching memories: {e}")
            session_based_memories = {'results': []}

    context = "<MEMORY>Relevant information from previous conversations:\n"   

    for session_memory in session_based_memories.get('results', []):
        context += f"Session Memory: {session_memory['memory']}\n"

    if state["signed_in"] and 'global_memories' in locals():
        for global_memory in global_memories.get('results', []):
            context += f"Global Memory of the User: {global_memory['memory']}\n"

    state['context'] = context + "</MEMORY>"
    logger.info("Memories Extracted")

    return {"context": state['context']}

# def chatbot(state: ChatbotState):
#     messages = state["messages"]
#     user_id = state["mem0_user_id"]
#     run_id = state["mem0_session_id"]

#     try:

#         llm = init_chat_model(model="openai:gpt-4.1-mini", api_key=os.getenv("OPENAI_API_KEY"))
#         llm2 = init_chat_model(model="anthropic:claude-4-5-haiku-latest", api_key=os.getenv("ANTHROPIC_API_KEY"))

#         system_message_content = system_prompt_template.format(query=messages[-1].content, context=state['context'])
#         system_message = SystemMessage(content=system_message_content)

#         # Prepare user message content (Text only as requested)
#         user_message = HumanMessage(content=messages[-1].content)
        
#         # Let's be safer:
#         history = messages[:-1][-6:] if len(messages) > 1 else []
#         full_messages = [system_message] + history + [user_message]

#         response = llm.invoke(full_messages)

#         # Store the interaction in Mem0
#         try:
#             # Handle image storage if present (new logic)
#             if state.get("image_data"):
#                 image_message = {
#                     "role": "user",
#                     "content": {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": f"data:image/jpeg;base64,{state['image_data']}"
#                         }
#                     }
#                 }
#                 client.add([image_message], user_id=user_id, run_id=run_id)
#                 logger.info("Image memory saved")

#             interaction = [
#                 {
#                     "role": "user",
#                     "content": messages[-1].content
#                 },
#                 {
#                     "role": "assistant", 
#                     "content": response.content
#                 }
#             ]
#             result = client.add(interaction, user_id=user_id, run_id=run_id)
#             logger.info(f"Text Interaction memory saved: {len(result.get('results', []))} memories added")
#         except Exception as e:
#             logger.error(f"Error saving memory: {e}")
            
#         return {"messages": [response]}
        
#     except Exception as e:
#         logger.error(f"Error in chatbot: {e}")
#         # Fallback response without memory context
#         response = llm.invoke(messages)
#         return {"messages": [response]}

async def chatbot(state: ChatbotState):
    messages = state["messages"]
    user_id = state["mem0_user_id"]
    run_id = state["mem0_session_id"]
    context = state.get("context", "")

    try:
        query = messages[-1].content
        # Combine user query with memory context for the agent
        full_query = f"Memory Context: {context}\n\nMessages History: {messages}\n\nUser Query: {query}\n\n"
        
        result = await Runner.run(main_agent, full_query)
        response_content = result.final_output
        
        # Store the interaction in Mem0
        try:
            # Handle image storage if present
            if state.get("image_data"):
                image_message = {
                    "role": "user",
                    "content": {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{state['image_data']}"
                        }
                    }
                }
                client.add([image_message], user_id=user_id, run_id=run_id)
                logger.info("Image memory saved")

            interaction = [
                {
                    "role": "user",
                    "content": query
                },
                {
                    "role": "assistant", 
                    "content": response_content
                }
            ]
            client.add(interaction, user_id=user_id, run_id=run_id)
            logger.info("Interaction memory saved")
        except Exception as e:
            logger.error(f"Error saving memory: {e}")

        response = AIMessage(content=response_content)
        return {"messages": [response]}

    except Exception as e:
        logger.error(f"Error in chatbot: {e}")
        # Fallback
        return {"messages": [AIMessage(content="I'm sorry, I encountered an error processing your request.")]}
        


graph_builder = StateGraph(ChatbotState)

graph_builder.add_node("get_memories", get_memories)
graph_builder.add_node("chatbot", chatbot)


graph_builder.add_edge(START, "get_memories")
graph_builder.add_edge("get_memories", "chatbot")
graph_builder.add_edge("chatbot", "get_memories")

compiled_graph = graph_builder.compile()

async def run_conversation(user_input: str, mem0_user_id: str, mem0_session_id: str, signed_in: bool, image_data: str | None = None):
    config = {"configurable": {"thread_id": mem0_user_id}}
    state = {
                "messages": [HumanMessage(content=user_input)], 
                "mem0_user_id": mem0_user_id,
                "mem0_session_id": mem0_session_id,
                "signed_in": signed_in,
                "image_data": image_data,
                "context": ""
            }

    async for event in compiled_graph.astream(state, config):
        for value in event.values():
            if value and value.get("messages"):
                return value["messages"][-1].content

async def main():
    print("Welcome to DHS 2026! How can I assist you today?")   
    mem0_user_id = "skh"  # You can generate or retrieve this based on your user management system
    mem0_session_id = "skh-001"  # You can generate or retrieve this based on your user management system
    signed_in = True
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Thank you for contacting us. Have a great day!")
            break
        response = await run_conversation(user_input, mem0_user_id, mem0_session_id, signed_in)
        print("Customer Support:", response)

if __name__ == "__main__":
    asyncio.run(main())