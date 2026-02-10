import asyncio

from agents import Agent, Runner, function_tool, SQLiteSession

from agents import (
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)
from pydantic import BaseModel

from prompts import *
# set_tracing_disabled
from mem0 import MemoryClient
import os
from dotenv import load_dotenv

from prompts import *

load_dotenv()

client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))

class IsDHSRelevant(BaseModel):
    is_dhs_relevant: bool
    reasoning: str

guardrail_agent = Agent( 
    name="Guardrail check",
    instructions="""You are the DHS 2026 AI Assistant. Check if the user is asking you to do something related to DHS 2026.

    Remember, salutations, grettings, of such conversation should be allowed

    The user query should revolve around the following topics:
    - DHS 2026 overview and themes
    - Schedule and agenda highlights
    - Speakers and Workshops
    - Registration, venue, and logistics
    - Networking and learning opportunities
    - Fun activities at the event
    - Location of the DHS Sessions and Workshops
    - Dates and timings related to the events 

    Be Lenient in your responses

    Anything else from these topics then we should politely refuse to answer or redirect them back the the DHS topic
    """,
    output_type=IsDHSRelevant,
)

@input_guardrail
async def dhs_guardrail( 
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output, 
        tripwire_triggered=not result.final_output.is_dhs_relevant,
    )

@function_tool
async def agenda_information(query: str) -> str:
    agenda_agent = Agent(
        name = "DHS Agenda Agent",
        instructions = agenda_agent_prompt,
        model="gpt-4.1-mini",
    )

    result = await Runner.run(agenda_agent, query)
    # print(result.final_output)

    return result.final_output

@function_tool
async def session_information(query: str) -> str:
    session_agent = Agent(
        name = "DHS Session Agent",
        instructions = session_agent_prompt,
        model="gpt-4.1-mini",
    )

    result = await Runner.run(session_agent, query)
    # print(result.final_output)

    return result.final_output

@function_tool
async def speakers_information(query: str) -> str:
    speaker_agent = Agent(
        name = "DHS Session Agent",
        instructions = speaker_agent_prompt,
        model="gpt-4.1-mini",
    )

    result = await Runner.run(speaker_agent, query)
    # print(result.final_output)

    return result.final_output

@function_tool
async def workshop_information(query: str) -> str:
    workshop_agent = Agent(
        name = "DHS Session Agent",
        instructions = workshop_agent_prompt,
        model="gpt-4.1-mini",
    )

    result = await Runner.run(workshop_agent, query)
    # print(result.final_output)

    return result.final_output





def get_main_agent(memory_context: str, messages: list) -> Agent:
    return Agent(
        name = "DHS Agent",
        instructions = main_agent_prompt.format(memory_context=memory_context, messages=messages),
        model = "gpt-4.1-mini",
        tools = [agenda_information, session_information, speakers_information, workshop_information],
        input_guardrails=[dhs_guardrail]
    )

async def main(query):
    # For standalone testing, pass empty context and history
    agent = get_main_agent("", [])
    result = await Runner.run(agent, query)
    # print(result.final_output)

    return result.final_output

if __name__ == "__main__":
    asyncio.run(main("tell me about any sessions which explain transfromers in detail"))


