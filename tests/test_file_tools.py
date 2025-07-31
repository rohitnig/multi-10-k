# tests/test_file_tools.py

import pytest
from unittest.mock import MagicMock

# The function we are testing
from app.tools.file_tools import query_10k_report

@pytest.fixture
def mock_tool_state(mocker):
    """
    This pytest fixture uses the 'mocker' utility to replace all external
    dependencies within our tool's 'tool_state' object.
    """
    # 1. Mock the main state object
    mock_state = MagicMock()

    # 2. Mock the embedding model
    mock_embedding_model = MagicMock()
    mock_embedding_model.encode.return_value.tolist.return_value = [0.1] * 384 # Dummy embedding
    mock_state.get_embedding_model.return_value = mock_embedding_model

    # 3. Mock the ChromaDB collection
    mock_collection = MagicMock()
    # Simulate a successful ChromaDB query result
    mock_collection.query.return_value = {
        'documents': [['This is a retrieved chunk about Google revenue.', 'This is another chunk.']]
    }
    mock_state.get_collection.return_value = mock_collection

    # 4. Mock the Gemini generation model
    mock_generation_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Based on the 10-K, Google's revenue was significant." # Our final mocked answer
    mock_generation_model.generate_content.return_value = mock_response
    mock_state.get_generation_model.return_value = mock_generation_model
    
    # 5. Use mocker.patch to replace the actual tool_state in the file with our mock
    mocker.patch('app.tools.file_tools.tool_state', mock_state)
    
    return mock_state


def test_query_10k_report_successful(mock_tool_state):
    """
    Tests the happy path of the query_10k_report tool using mocked dependencies.
    """
    # Arrange: The mock_tool_state fixture has already set everything up.
    question = "What was Google's revenue in 2023?"

    # Act: Run the tool function.
    result = query_10k_report(question)

    # Assert: Check that the result is what we expect from our mocked Gemini call.
    assert result == "Based on the 10-K, Google's revenue was significant."

    # Bonus Asserts: We can also verify that our mocks were used correctly.
    # Check that the embedding model was called with our question.
    mock_tool_state.get_embedding_model().encode.assert_called_with(question)
    
    # Check that the database was queried.
    mock_tool_state.get_collection().query.assert_called_once()

    # Check that the generative model was called.
    mock_tool_state.get_generation_model().generate_content.assert_called_once()
    
    print("\n✅ Test Passed: `query_10k_report` successfully returned the mocked response.")
