import asyncio
from agent_sdk import get_main_agent, Runner
import logging

async def reproduce():
    # Mock context and messages
    context = ""
    messages = []
    query = "Who is the prime minister of India?"
    
    agent = get_main_agent(context, messages)
    
    try:
        result = await Runner.run(agent, query)
        print(f"Result type: {type(result)}")
        print(f"Input guardrail results type: {type(result.input_guardrail_results)}")
        if result.input_guardrail_results:
            print(f"First element type: {type(result.input_guardrail_results[0])}")
            print(f"First element dir: {dir(result.input_guardrail_results[0])}")
            # Try to see what attributes it has
            try:
                print(f"First element message: {result.input_guardrail_results[0].message}")
            except Exception as e:
                print(f"Error accessing .message: {e}")
    except Exception as e:
        print(f"Caught exception: {type(e).__name__}: {e}")
        # Inspect the exception attributes
        print(f"Attributes of {type(e).__name__}: {dir(e)}")
        
        # In openai-agents, the exception often has the result
        if hasattr(e, 'result'):
            result = e.result
            print(f"Result in exception: {result}")
            print(f"Input guardrail results: {result.input_guardrail_results}")
            if result.input_guardrail_results:
                for idx, res in enumerate(result.input_guardrail_results):
                    print(f"Result {idx} type: {type(res)}")
                    print(f"Result {idx} dir: {dir(res)}")
                    # Common attributes in InputGuardrailResult
                    for attr in ['message', 'output', 'triggered', 'output_info']:
                        if hasattr(res, attr):
                            print(f"  {attr}: {getattr(res, attr)}")


if __name__ == "__main__":
    asyncio.run(reproduce())
