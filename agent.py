from typing import Annotated, TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from mem0 import MemoryClient, Memory
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from pydantic import BaseModel
from datetime import datetime
import time

from config import *

# from helper import add_memory, search_memory
from prompts import * 

from agent_sdk import (
    get_main_agent, 
    Runner, 
    get_agenda_information, 
    get_session_information, 
    get_speakers_information, 
    get_workshop_information
)
import asyncio

import logging

import os
from dotenv import load_dotenv

load_dotenv(override=True)

from logger import logger
logger.setLevel(logging.INFO)

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": os.getenv("QDRANT_COLLECTION_NAME"),
            "url": os.getenv("QDRANT_URL"),
            "api_key": os.getenv("QDRANT_API_KEY"),
        }
    }
}

# client = MemoryClient(api_key=os.getenv("MEM0_API_KEY")).from_config(config)
client = Memory().from_config(config)

class ChatbotState(TypedDict):
    memory: Dict[str, Any]
    mem0_user_id: str
    mem0_session_id: str
    context: str

    signed_in: bool
    image_data: str | None
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]

    start_time: float
    end_time: float

class GuardrailResponse(BaseModel):
    guardrail_response: bool
    reasoning: str

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

    state['start_time'] = time.time()


    logger.info(f"User ID: {user_id}")
    logger.info(f"Run ID: {run_id}")
    logger.info(f"Signed In: {state['signed_in']}")
    
    if state["signed_in"]:
        logger.info("Getting Session and Global Memories")
        try:
            # Session-based memories using run_id
            # session_based_memories = client.search(
            #     messages[-1].content, 
            #     filters={"AND": [{"user_id": user_id}, {"run_id": run_id}]}
            # )
            session_based_memories = client.search(
                messages[-1].content, 
                user_id=user_id,
                run_id=run_id
            )

            print("---Session Memories---")
            print(session_based_memories)
            print()
            # Global memories for user
            search_query = "Retrieve all existing memories related to this user query " + messages[-1].content + "or existing memories of previous conversations"
            try:
                # global_memories = client.search(
                #     search_query, 
                #     filters={"user_id": user_id},
                #     limit=10
                # )
                global_memories = client.search(
                    search_query, 
                    user_id=user_id,
                    limit=10
                )

                print("---Global Memories---")
                print(global_memories)
                print()
            except Exception as e:
                logger.error(f"Error fetching global memories: {e}")
                global_memories = {'results': []}
        except Exception as e:
            logger.error(f"Error fetching memories: {e}")
            session_based_memories = {'results': []}
            global_memories = {'results': []}
    else:
        logger.info("Getting Session Memories only")
        try:
            # session_based_memories = client.search(
            #     messages[-1].content, 
            #     filters={"AND": [{"user_id": user_id}, {"run_id": run_id}]}
            # )
            session_based_memories = client.search(
                messages[-1].content, 
                user_id=user_id,
                run_id=run_id
            )
        except Exception as e:
            logger.error(f"Error fetching memories: {e}")
            session_based_memories = {'results': []}

    state['context'] = "PAST MEMORY \n The AHA moment we spoke about this Memories you have of the user from previous conversations:\n"   

    for session_memory in session_based_memories.get('results', []):
        state['context'] += f"Session Memory: {session_memory['memory']}\n"

    if state["signed_in"] and 'global_memories' in locals():
        for global_memory in global_memories.get('results', []):
            state['context'] += f"Global Memory of the User: {global_memory['memory']}\n"

    logger.info("Memories Extracted")

    query = messages[-1].content
    # Parallel execution of tools
    agenda, session, speakers, workshop = await asyncio.gather(
        get_agenda_information(query),
        get_session_information(query),
        get_speakers_information(query),
        get_workshop_information(query)
    )

    state['context'] += f"""This are some information which we have got from the tools.\n

        REMEMBER SESSIONS AND WORKSHOPS ARE DIFFERENT

        These are the Agenda Information ONLY {agenda}\n"
        These are the Session Information ONLY {session}\n"
        These are the speakers Infromation ONLY {speakers}\n
        These are the Workshops Information ONLY {workshop}
        """
    
    logger.info("Tools Information Extracted")

    return {"context": state['context'], "start_time": state['start_time']}

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

    query = messages[-1].content

    # agent = get_main_agent(context, messages)
    
    guardrail_llm = init_chat_model(
        model="openai:gpt-4.1-mini", 
        api_key=os.getenv("OPENAI_API_KEY")
    ).with_fallbacks([
        init_chat_model(model="anthropic:claude-4-5-haiku-latest", api_key=os.getenv("ANTHROPIC_API_KEY"))
    ])

    llm = init_chat_model(
        model="openai:gpt-4.1-mini", 
        api_key=os.getenv("OPENAI_API_KEY")
    ).with_fallbacks([
        init_chat_model(model="anthropic:claude-4-5-haiku-latest", api_key=os.getenv("ANTHROPIC_API_KEY"))
    ])

    # Use the specific prompt templates
    prompt, guardrail_prompt = main_agent_prompt.format(memory_context=context, messages=messages), guardrail_prompt_template.format(query=query, messages=messages)

    try:
        # Execute both LLM calls in parallel
        response_task = llm.ainvoke(prompt)
        # Use invoke instead of ainvoke if with_structured_output doesn't support ainvoke or for simpler call
        # but better to use ainvoke if possible
        guardrail_task = guardrail_llm.with_structured_output(GuardrailResponse).ainvoke(guardrail_prompt)

        response, guardrail_response = await asyncio.gather(response_task, guardrail_task)

        end_time = time.time()
        state['end_time'] = end_time
        logger.info(f"Time taken: {end_time - state['start_time']}")
        
        response_content = response.content
        guardrail_relevant = guardrail_response.guardrail_response

        if guardrail_relevant:
            # Store the interaction in Mem0
            try:
                if state.get("image_data"):
                    image_message = {
                        "role": "user",
                        "content": {
                            "type": "image_url",
                            "image_url": { "url": f"data:image/jpeg;base64,{state['image_data']}" }
                        }
                    }
                    client.add([image_message], user_id=user_id, run_id=run_id)
                    logger.info("Image memory saved")

                # interaction = [
                #     {"role": "user", "content": query},
                #     {"role": "assistant", "content": response_content}
                # ]

                interaction = [
                    {"role": "assistant", "content": response_content}
                ]

                client.add(interaction, user_id=user_id, run_id=run_id, infer=False)
                logger.info("Interaction memory saved")

            except Exception as e:
                logger.error(f"Error saving image memory: {e}")

            return {"messages": [AIMessage(content=response_content)], "end_time": state['end_time']}
        
        else:
            # If not relevant, return the reasoning (the refusal message)
            return {"messages": [AIMessage(content=guardrail_response.reasoning)], "end_time": state['end_time']}

    except Exception as e:
        logger.error(f"Error in chatbot: {e}")
        # Fallback
        return {"messages": [AIMessage(content="I'm sorry, I'm having trouble processing your request right now. Could you please rephrase your query?")]}
        


graph_builder = StateGraph(ChatbotState)

graph_builder.add_node("get_memories", get_memories)
graph_builder.add_node("chatbot", chatbot)


graph_builder.add_edge(START, "get_memories")
graph_builder.add_edge("get_memories", "chatbot")
graph_builder.add_edge("chatbot", "get_memories")

compiled_graph = graph_builder.compile()

async def run_conversation(user_input: str, mem0_user_id: str, mem0_session_id: str, signed_in: bool | None = None, image_data: str | None = None):
    # Derive signed_in from mem0_user_id if not provided
    # if signed_in is None:
    #     signed_in = bool(mem0_user_id and mem0_user_id.strip())
    
    config = {"configurable": {"thread_id": mem0_user_id}}
    state = {
                "messages": [HumanMessage(content=user_input)], 
                "mem0_user_id": mem0_user_id,
                "mem0_session_id": mem0_session_id,
                "signed_in": signed_in,
                "image_data": image_data,
                "context": "",
                "start_time": 0.0,
                "end_time": 0.0
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