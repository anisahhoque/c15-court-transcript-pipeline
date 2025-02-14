"""This file extracts data from xmls using OpenAI API"""
import json
import logging

from os import environ as ENV
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from pydantic import BaseModel

load_dotenv()



class Judge(BaseModel):
    """Represents a judge involved in a legal case."""
    judge_name: str

class Legislation(BaseModel):
    """Represents legislations referenced in the judgment"""
    legislation_name: str
    legislation_section: str

class Judgment(BaseModel):
    """Reference/unique id for a judgment"""
    neutral_citation: str

class Argument(BaseModel):
    summary: str
    judgments_referenced: list[Judgment]
    legislations_referenced: list[Legislation]

class Counsel(BaseModel):
    """Represents a counsel for a party"""
    counsel_name: str
    counsel_title: str
    chamber_name: str


class Party(BaseModel):
    """Represents a party involved in a legal case."""
    party_name: str
    party_role: str
    counsels: list[Counsel]
    arguments: list[Argument]


class CaseOutput(BaseModel):
    """All details to be extracted from the xmls"""
    type_of_crime: str
    description: str
    judge: list[Judge]
    parties: list[Party]

class JudgmentOutput(BaseModel):
    """Returns all information in a case summary"""
    case_summary: list[CaseOutput]


def get_client() -> OpenAI:
    """Returns a client for the API"""
    try:
        client = OpenAI(
        api_key=ENV.get("OPENAI_API_KEY"),
        timeout=10.0,
        )
        return client
    except OpenAIError as e:
        logging.error('Failed to return an OpenAI client - %s', str(e))


def get_list_xml_data(filenames: list[str]) -> list[str]:
    """Reads xmls and returns a list of strings with the xml data"""
    cases = []
    for file in filenames:
        with open(file, 'r', encoding='UTF-8') as file:
            cases.append(file.read())
    return cases

def get_case_summaries(model: str, client: OpenAI, prompt: str) -> list[dict]:
    """Returns a list of dictionaries for each xml with the relevant data"""
    try:
        response = client.with_options(timeout=60).beta.chat.completions.parse(
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
        data = json.loads(response_choices.content).get("case_summary")

        with open('gpt2_response.json','w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
            
        return data

    except OpenAIError as e:
        logging.error('An error occurred while trying to retrieve case information - %s', str(e))

if __name__=="__main__":
    api_client = get_client()
    GPT_MODEL = "o3-mini"
    file_names = ['ewhc_comm_2025_240.xml','ukut_iac_2021_202.xml','ewcop_t3_2025_6.xml']
    list_of_cases = get_list_xml_data(filenames=[file_names[1]])
    PROMPT = f"""
    I have a list of court case transcriptions:
    {list_of_cases}
    You are a lawyer reading judgment transcripts.
    Please analyse each case and return a summary for each.

    Give me a summary for each of the cases provided. Your response should be in a list of dictionaries containing the following keys:
    - type_of_crime: criminal or civil 
    - description: a short neutral summary of the trial
    - judge: The fullname of the judge including the title e.g Mr Justice Smith
    - parties: A list of all parties involved in the case, with the following details for each party:
        - name: The name of the party.
        - role: The role of the party (e.g., "plaintiff", "defendant", "appellant", "respondent").
        - counsels: A list of counsel(s) for the party, with the following details for each counsel:
            - name: The name of the counsel (e.g., "William Bennett KC").
            - title: The title of the counsel (e.g., "KC", "QC", or none).
            - chamber: The name of the counsel's chambers (e.g., "Brett Wilson LLP").
        - arguments: A list of unique arguments, claims, or submissions made by the party. For each argument, include:
            - A brief summary of the argument presented
            - a list of references(neutral citations) that are mentioned in that specific argument
            - a list of legislations that are mentioned in that specific argument
            - legislations have a legislation name and section for example Data Protection Act 2018 Section 17, if no section is specified then label as All



    This MUST be a json and only be a list of dictionaries
    """

    get_case_summaries(model=GPT_MODEL,client=api_client,prompt=PROMPT)
