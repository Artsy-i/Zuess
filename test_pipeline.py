import pytest
from unittest.mock import patch, MagicMock

from orchestrator import ZeussOrchestrator
from llm_router import LLMRouter

@patch('orchestrator.requests.post')
def test_orchestrator_call_llm(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {"message": {"content": "RUN_NODE_A(1)"}}
        ]
    }
    mock_post.return_value = mock_response

    orch = ZeussOrchestrator("AI Supply Chain 2026")
    command = orch._call_llm()
    assert command == "RUN_NODE_A(1)"

@patch('llm_router.LLMRouter.execute_with_waterfall')
def test_llm_router_execute_with_waterfall(mock_execute):
    mock_execute.return_value = "Mocked response from llm."
    router = LLMRouter()
    output = router.execute_with_waterfall(task_prompt="Test task")
    assert output == "Mocked response from llm."


@patch('openai.OpenAI')
@patch('llm_router.LLMRouter._resolve_api_key')
def test_openai_direct(mock_resolve, mock_openai_class):
    mock_resolve.return_value = "fake_key"

    mock_client = MagicMock()
    mock_response_chunk1 = MagicMock()
    mock_response_chunk1.choices = [MagicMock(delta=MagicMock(content="Mocked "))]
    mock_response_chunk2 = MagicMock()
    mock_response_chunk2.choices = [MagicMock(delta=MagicMock(content="response from llm."))]

    # Needs to be iterable since stream=True
    mock_client.chat.completions.create.return_value = [mock_response_chunk1, mock_response_chunk2]
    mock_openai_class.return_value = mock_client

    router = LLMRouter()
    output = router.execute_with_waterfall(task_prompt="Test task")
    assert output == "Mocked response from llm."
