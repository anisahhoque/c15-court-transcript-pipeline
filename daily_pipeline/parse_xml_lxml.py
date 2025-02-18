"""Script to parse xml file for information prior to use of AI."""

from lxml import etree


def parse_xml(file_path: str) -> dict:
    """Parses judgment xml, returning a dict. Example output below"
    {'neutral_citation_number': '[2025] UKFTT 124 (GRC)',
    'parties': [{'party_name': 'Mustafa aktekin', 'party_role': 'appellant'},
    {'party_name': 'REGISTRAR FOR APPROVED DRIVING INSTRUCTORS', 'party_role': 'respondent'}],
    'judgment_date': '2025-02-11',
    'court_name': 'UKFTT-GRC'}"""
    tree = etree.parse(file_path)
    root = tree.getroot()

    namespaces = {
        "akn": "http://docs.oasis-open.org/legaldocml/ns/akn/3.0",
        "uk": "https://caselaw.nationalarchives.gov.uk/akn"
    }

    metadata = {}

    cite = root.xpath("//uk:cite", namespaces=namespaces)

    metadata["neutral_citation_number"] = cite[0].text


    parties = root.xpath("//akn:party", namespaces=namespaces)
    parties = [
        {"party_name": party.text.strip(), "party_role": party.get("as").strip("#")}
        for party in parties
    ]

    metadata["parties"] = parties

    judgment_date = root.xpath("//akn:FRBRExpression/akn:FRBRdate/@date", namespaces=namespaces)
    judgment_date = judgment_date[0] if judgment_date else "Not found"

    metadata["judgment_date"] = judgment_date

    court_info = root.xpath("//uk:court/text()", namespaces=namespaces)

    court_name = court_info[0] if court_info else "Not found"

    metadata["court_name"] = court_name

    return metadata


if __name__ == "__main__":
    print(parse_xml("ukftt_grc_2025_124.xml"))