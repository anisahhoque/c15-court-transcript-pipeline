#pylint:disable=unused-variable
"""This file extracts data from xmls using OpenAI API"""
import json
import logging
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from pydantic import BaseModel

load_dotenv()

GPT_MODEL = "gpt-4o-mini"


class Counsel(BaseModel):
    """Represents a counsel for a party"""
    counsel_name: str
    chamber_name: str

class Party(BaseModel):
    """Represents a party involved in a legal case."""
    party_name: str
    party_role: str
    counsels: list[Counsel]

class CaseOutput(BaseModel):
    """All details to be extracted from the xmls"""
    type_of_crime: str
    judgment_description: str
    judge: str
    parties: list[Party]
    ruling: str

class JudgmentOutput(BaseModel):
    """Returns all information in a case summary"""
    case_summary: CaseOutput


def get_client(api_key: str) -> OpenAI:
    """Returns a client for the API"""
    try:
        client = OpenAI(
        api_key=api_key,
        timeout=10.0
        )
        return client
    except OpenAIError as e:
        logging.error('Failed to return an OpenAI client - %s', str(e))


def get_xml_data(filename: str) -> str:
    """Reads an xml and returns a string with the xml data"""
    with open(filename, 'r', encoding='UTF-8') as file:
        return file.read()[:100000]

def get_case_summary(model: str, client: OpenAI, case: str) -> dict:
    """Returns a dictionary for a judgment containing summary information"""
    prompt = f"""

    You are a lawyer reading judgment transcripts.
    Please analyse the judgment and return a summary from the case data I provide.
    The transcript: {case}
    Your response should be in a list of dictionaries containing the following keys:
    - type_of_crime: criminal or civil 
    - judgment_description: a summary of the judgment
    - parties: A list of all parties involved in the case, with the following details for each party:
        - name: The name of the party.
        - role: The role of the party.
        - counsels: A list of counsel(s) for the party, with the following details for each counsel:
            - name: The name of the counsel (e.g., "William Bennett KC").
            - title: The title of the counsel (e.g., "KC", "QC", or none).
            - chamber: The name of the counsel's chambers (e.g., "Brett Wilson LLP").
    - judge: The fullname of the judge including the title e.g Mr Justice Smith
    - ruling: the party role in which the judgment is in favour of (just the party role, no need for a full sentence, and it must match one of the party roles, exact same spelling and matching singular/plural)


    This MUST be a json.
    """
    try:
        response = client.with_options(timeout=60.0).beta.chat.completions.parse(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
        response_format=JudgmentOutput,
        )
        response_choices = response.choices[0].message

        return json.loads(response_choices.content).get("case_summary")

    except OpenAIError as e:
        logging.error('An error occurred while trying to retrieve case information - %s', str(e))
        return []
