"""Tests for prompts"""
import json
from unittest.mock import patch, Mock, mock_open
import pytest
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from prompt_engineering import get_client, get_xml_data, get_case_summary

SAMPLE_XML_1 = """<?xml version="1.0" encoding="UTF-8"?>
<judgment>
    <header>
        <court>High Court of Justice King's Bench Division</court>
        <address>Royal Courts of Justice, Strand, London, WC2A 2LL</address>
        <case_number>QB-2025-000287</case_number>
        <neutral_citation>[2025] EWHC 287 (KB)</neutral_citation>
        <date>14/02/2025</date>
    </header>
    <body>
        <parties>
            <party>
                <name>John Smith</name>
                <role>Claimant</role>
                <counsel>
                    <name>William Bennett</name>
                    <title>KC</title>
                    <chamber>Brett Wilson LLP</chamber>
                </counsel>
            </party>
        </parties>
        <judges>
            <judge>
                <name>Pepperall</name>
                <title>Mr Justice</title>
                <jurisdiction>England and Wales</jurisdiction>
            </judge>
        </judges>
        <legislation>Criminal Justice Act 2003</legislation>
    </body>
</judgment>"""

SAMPLE_XML_2 = """<?xml version="1.0" encoding="UTF-8"?>
<judgment>
    <header>
        <court>High Court of Justice Commercial Court</court>
        <address>7 Rolls Building, Fetter Lane, London, EC4A 1NL</address>
        <case_number>CL-2025-000240</case_number>
        <neutral_citation>[2025] EWHC 240 (Comm)</neutral_citation>
        <date>10/02/2025</date>
    </header>
    <body>
        <parties>
            <party>
                <name>ABC Corporation</name>
                <role>Defendant</role>
                <counsel>
                    <name>Sarah James</name>
                    <title>KC</title>
                    <chamber>Matrix Chambers</chamber>
                </counsel>
            </party>
        </parties>
        <judges>
            <judge>
                <name>Bright</name>
                <title>Mrs Justice</title>
                <jurisdiction>England and Wales</jurisdiction>
            </judge>
        </judges>
        <legislation>Companies Act 2006</legislation>
    </body>
</judgment>"""

SAMPLE_RESPONSE_DATA = {
    "case_summary": [
        {
            "date": "14/02/2025",
            "type_of_crime": "civil",
            "description": "Contract dispute between parties",
            "parties": [
                {
                    "party_name": "John Smith",
                    "party_role": "Claimant",
                    "counsels": [
                        {
                            "counsel_name": "William Bennett",
                            "counsel_title": "KC",
                            "chamber_name": "Brett Wilson LLP"
                        }
                    ]
                }
            ],
            "judge": [
                {
                    "judge_name": "Pepperall",
                    "jurisdiction_name": "England and Wales",
                    "judge_title": "Mr Justice"
                }
            ],
            "legislations": [
                {
                    "legislation_name": "Civil Procedure Rules"
                }
            ],
            "neutral_citation": {
                "neutral_citation": "[2025] EWHC 287 (KB)"
            },
            "court_name": "High Court of Justice King's Bench Division",
            "court_address": "Royal Courts of Justice, Strand, London, WC2A 2LL",
            "case_number": "QB-2025-000287",
            "referenced_judgements": [
                {
                    "neutral_citation": "[2024] EWHC 123 (KB)"
                }
            ]
        }
    ]
}

@pytest.fixture
def mock_openai_client():
    """Fixture providing a mock OpenAI client"""
    mock_client = Mock(spec=OpenAI)
    mock_message = Mock(spec=ChatCompletionMessage)
    mock_message.content = json.dumps(SAMPLE_RESPONSE_DATA)
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_response = Mock(spec=ChatCompletion)
    mock_response.choices = [mock_choice]
    mock_client.with_options.return_value.beta.chat.completions.parse.return_value = mock_response
    return mock_client

def test_get_client_return_type():
    """Test that get_client returns an OpenAI instance"""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        client = get_client()
        assert isinstance(client, OpenAI)


def test_get_list_xml_data_multiple_files():
    """Test reading multiple XML files"""
    mock_files = {
        'test1.xml': SAMPLE_XML_1,
        'test2.xml': SAMPLE_XML_2
    }
    def mock_open_files(filename, mode, encoding):
        return mock_open(read_data=mock_files[filename]).return_value
    
    with patch('builtins.open', mock_open_files):
        result = get_list_xml_data(['test1.xml', 'test2.xml'])
        assert len(result) == 2
        assert result[0] == SAMPLE_XML_1
        assert result[1] == SAMPLE_XML_2

def test_get_list_xml_data_return_type():
    """Test return type annotations and actual return type"""
    with patch('builtins.open', mock_open(read_data=SAMPLE_XML_1)):
        result = get_xml_data(['test1.xml'])
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)

def test_get_case_summaries_successful_call(mock_openai_client):
    """Test successful API call and response parsing"""
    result = get_case_summary(
        model="test-model",
        client=mock_openai_client,
        prompt="Test prompt"
    )

    mock_openai_client.with_options.assert_called_once_with(timeout=60.0)
    mock_openai_client.with_options.return_value.beta.chat.completions.parse.assert_called_once()

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["court_name"] == "High Court of Justice King's Bench Division"
    assert result[0]["case_number"] == "QB-2025-000287"

def test_get_case_summaries_data_structure(mock_openai_client):
    """Test the structure of returned data matches expected schema"""
    result = get_case_summary(
        model="test-model",
        client=mock_openai_client,
        prompt="Test prompt"
    )

    case = result[0]

    assert all(key in case for key in [
        "date", "type_of_crime", "description", "parties",
        "judge", "legislations", "neutral_citation",
        "court_name", "court_address", "case_number",
        "referenced_judgements"
    ])

    assert isinstance(case["parties"], list)
    assert isinstance(case["judge"], list)
    assert isinstance(case["legislations"], list)
    assert isinstance(case["referenced_judgements"], list)
