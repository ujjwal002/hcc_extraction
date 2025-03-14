import pytest
from unittest.mock import Mock
from src.hcc_pipeline.core.extraction import extract_conditions

@pytest.fixture
def mock_model():
    model = Mock()
    model.generate_content.return_value.text = '''
    [{"condition": "Diabetes", "code": "E11"}]
    '''
    return model

def test_extraction_success(mock_model):
    text = "Assessment/Plan: Diabetes (E11.9)"
    result = extract_conditions(text, mock_model)
    assert len(result) == 1
    assert result[0]["code"] == "E11"

def test_empty_assessment_section():
    text = "No relevant sections here"
    result = extract_conditions(text, Mock())
    assert len(result) == 0