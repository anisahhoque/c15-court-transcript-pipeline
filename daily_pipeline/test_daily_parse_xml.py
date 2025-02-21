import pytest
import logging
from unittest.mock import mock_open, patch
import unittest
import os

from bs4 import BeautifulSoup

from daily_parse_xml import get_metadata, convert_judgment


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


class TestConvertJudgment(unittest.TestCase):

    def setUp(self):
        self.html_folder_path = 'test_html_folder'
        self.xml_file_path = 'test_file.xml'
        self.xml_file_name = 'test_file.xml'

        self.sample_xml_content = """<root>
            <judgmentBody>
                <p>Judgment content goes here.</p>
            </judgmentBody>
        </root>"""

        with open(self.xml_file_path, 'w', encoding='UTF-8') as f:
            f.write(self.sample_xml_content)

    def tearDown(self):
        if os.path.exists(self.html_folder_path):
            for file in os.listdir(self.html_folder_path):
                os.remove(os.path.join(self.html_folder_path, file))
            os.rmdir(self.html_folder_path)
        if os.path.exists(self.xml_file_path):
            os.remove(self.xml_file_path)

    def test_convert_judgment(self):
        convert_judgment(self.html_folder_path, self.xml_file_path, self.xml_file_name)

        html_file_path = os.path.join(self.html_folder_path, 'test_file.html')
        self.assertTrue(os.path.exists(html_file_path))

        with open(html_file_path, 'r', encoding='UTF-8') as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
            judgment_body = soup.find('p')
            self.assertIsNotNone(judgment_body)
            self.assertEqual(judgment_body.text, 'Judgment content goes here.')

