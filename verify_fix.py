import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch
from agent import chatbot, ChatbotState, GuardrailResponse
from langchain_core.messages import HumanMessage, AIMessage

async def test_chatbot_fixes():
    print("Starting verification of chatbot fixes...")

    # Mock State
    state: ChatbotState = {
        "messages": [HumanMessage(content="Hello, tell me about DHS 2026")],
        "mem0_user_id": "test_user",
        "mem0_session_id": "test_session",
        "context": "Previous interest in AI",
        "signed_in": True,
        "image_data": None,
        "start_time": 1000.0,
        "end_time": 0.0
    }

    # Mock LLM and Guardrail LLM
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="Here is some info about DHS 2026"))
    
    mock_guardrail_llm = MagicMock()
    mock_guardrail_llm.with_structured_output.return_value.ainvoke = AsyncMock(
        return_value=GuardrailResponse(guardrail_response=True, reasoning="Relevant to DHS")
    )

    with patch('agent.init_chat_model') as mock_init:
        # Mock init_chat_model to return our mocks
        # The code calls it twice: once for guardrail_llm, once for llm
        mock_init.return_value.with_fallbacks.side_effect = [mock_guardrail_llm, mock_llm]
        
        with patch('agent.client') as mock_mem0_client:
            print("--- Testing Relevant Query ---")
            result = await chatbot(state)
            print(f"Result: {result['messages'][0].content}")
            assert result['messages'][0].content == "Here is some info about DHS 2026"
            assert mock_mem0_client.add.called
            print("Relevant query test PASSED")

            # Test Irrelevant Query
            state["messages"] = [HumanMessage(content="What is the capital of France?")]
            mock_guardrail_llm.with_structured_output.return_value.ainvoke = AsyncMock(
                return_value=GuardrailResponse(guardrail_response=False, reasoning="French politics is not related to DHS 2026.")
            )
            
            print("\n--- Testing Irrelevant Query ---")
            result = await chatbot(state)
            print(f"Result: {result['messages'][0].content}")
            assert result['messages'][0].content == "French politics is not related to DHS 2026."
            print("Irrelevant query test PASSED")

            # Test Exception Handling
            mock_llm.ainvoke.side_effect = Exception("LLM Error")
            print("\n--- Testing Exception Handling ---")
            result = await chatbot(state)
            print(f"Result: {result['messages'][0].content}")
            assert "I'm sorry" in result['messages'][0].content
            print("Exception handling test PASSED")

    print("\nAll verification tests PASSED!")

if __name__ == "__main__":
    asyncio.run(test_chatbot_fixes())
