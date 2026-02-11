import asyncio
from agent_sdk import main

async def test_guardrail():
    print("Testing Guardrail with irrelevant query...")
    response = await main("Who is the prime minister of India?")
    print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(test_guardrail())
