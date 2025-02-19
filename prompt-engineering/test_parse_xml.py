import pytest
import logging
from unittest.mock import mock_open, patch
from parse_xml import get_metadata, get_all_metadata


@pytest.mark.parametrize(
    "xml_data, expected_metadata", [
        (
            """<judgment>
                <neutralCitation>2025 EWCA Civ 123</neutralCitation>
                <FRBRdate date="2025-02-15"/>
                <TLCOrganization showAs="High Court"/>
            </judgment>""",
            {
                'court_name': 'High Court',
                'neutral_citation': '2025 EWCA Civ 123',
                'judgment_date': '2025-02-15'
            }
        ),
        (
            """<judgment>
                <neutralCitation>2025 EWCA Civ 123</neutralCitation>
                <FRBRdate date="2025-02-15"/>
            </judgment>""",
            {
                'court_name': None,
                'neutral_citation': '2025 EWCA Civ 123',
                'judgment_date': '2025-02-15'
            }
        ),
        (
            """<judgment>
                <neutralCitation></neutralCitation>
                <FRBRdate date=""/>
                <TLCOrganization showAs=""/>
            </judgment>""",
            {
                'court_name': None,
                'neutral_citation': None,
                'judgment_date': None
            }
        ),
        (
            """<judgment></judgment>""",
            {
                'court_name': None,
                'neutral_citation': None,
                'judgment_date': None
            }
        ),
    ]
)

@patch("builtins.open", mock_open())
def test_get_metadata(xml_data, expected_metadata):
    with patch("builtins.open", mock_open(read_data=xml_data)):
        metadata = get_metadata("test_case.xml")
    
    assert metadata == expected_metadata


def test_file_not_found(caplog):

    with caplog.at_level(logging.ERROR):

        with patch('builtins.open', side_effect=FileNotFoundError):
            with pytest.raises(UnboundLocalError):  
                get_metadata('nonexistent.xml')
    

    assert 'File was not found - nonexistent.xml' in caplog.text


@patch('parse_xml.get_metadata')
def test_get_all_metadata(mock_get_metadata):
    mock_get_metadata.side_effect = [
        {
            'court_name': 'High Court',
            'neutral_citation': 'EWHC 123',
            'judgment_date': '2024-01-01'
        },
        {
            'court_name': 'Supreme Court',
            'neutral_citation': 'UKSC 456',
            'judgment_date': '2024-01-02'
        }
    ]
    
    result = get_all_metadata(['file1.xml', 'file2.xml'])
    
    assert len(result) == 2
    assert result[0]['court_name'] == 'High Court'
    assert result[1]['court_name'] == 'Supreme Court'
    
    assert mock_get_metadata.call_count == 2
