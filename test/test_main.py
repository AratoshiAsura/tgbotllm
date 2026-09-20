from ast import Return
from unittest import mock

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from main import ask_llm

@pytest.mark.asyncio
async def test_ask_llm_returns_content():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hi mock"

    with patch("main.client.chat.completions.create", new=AsyncMock(return_value=mock_response),):
        result = await ask_llm("test")

    assert result == "Hi mock"


@pytest.mark.asyncio
async def test_ask_llm_handles_error():
    with patch("main.client.chat.completions.create", new=AsyncMock(side_effect=Exception("API down")),):
        result = await ask_llm("test")


    assert "Error LLM" in result
