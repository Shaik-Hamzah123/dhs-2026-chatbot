import asyncio
from agent import run_conversation
import os
from dotenv import load_dotenv

load_dotenv()

async def verify():
    print("Verifying fix...")
    try:
        # Use a dummy user/session to avoid messing up real memories if possible, 
        # but we need to pass the mem0 filters which we fixed.
        response = await run_conversation("Hello, who are you?", "test_user_verification", "test_session_verification", True)
        print(f"Response: {response}")
        print("Verification SUCCESS")
    except Exception as e:
        print(f"Verification FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify())
