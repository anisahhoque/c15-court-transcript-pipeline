"""This file extracts data from xmls using OpenAI API"""
import json
import logging
from os import environ as ENV
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from pydantic import BaseModel

load_dotenv()

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

class Judge(BaseModel):
    """Represents a judge involved in a legal case."""
    judge_name: str
    judge_title: str

class Legislation(BaseModel):
    """Represents legislations referenced in the judgement"""
    legislation_name: str

class Judgement(BaseModel):
    """Reference/unique id for a judgement"""
    neutral_citation: str

class Argument(BaseModel):
    summary: str
    judgements_referenced: list[Judgement]
    legislations_referenced: list[Legislation]
    
class CaseOutput(BaseModel):
    """All details to be extracted from the xmls"""
    date: str
    hearing_dates: list[str]
    type_of_crime: str
    description: str
    parties: list[Party]
    judge: list[Judge]
    legislations: list[Legislation]
    neutral_citation: Judgement
    court_name: str
    court_address: str
    case_number: str
    referenced_judgements: list[Judgement]
    arguments: list[Argument]

class LawOutput(BaseModel):
    """Returns all information in a case summary"""
    case_summary: list[CaseOutput]

def print_case_details(case_data: dict) -> None:
    """
    Formats and prints case data in a clean, readable format
    """
    print("\n" + "="*50)
    print(f"CASE #{case_data['case_number']}")
    print(f"JUDGEMENT DATE {case_data['date']}")
    print("="*50 + "\n")

    print("COURT DETAILS")
    print("-"*30)
    print(f"Court: {case_data['court_name']}")
    print(f"Address: {case_data['court_address']}\n")

    print("CASE OVERVIEW")
    print("-"*30)
    print(f"Citation: {case_data['neutral_citation']['neutral_citation']}\n")
    print(f"Type of Crime: {case_data['type_of_crime']}")
    print(f"Description: {case_data['description']}\n")

    print("PARTIES INVOLVED")
    print("-"*30)
    for party in case_data['parties']:
        print(f"Name: {party['party_name']}")
        print(f"Role: {party['party_role']}")
        for counsel in party['counsels']:
            print(f"Counsel Name: {counsel['counsel_name']}")
            print(f"Counsel Title: {counsel['counsel_title']}")
            print(f"Chamber Name: {counsel['chamber_name']}")
        print()
    print()

    print("JUDGES")
    print("-"*30)
    for judge in case_data['judge']:
        print(f"Name: {judge['judge_name']}")
        print(f"Title: {judge['judge_title']}")
        print()

    print("RELEVANT LEGISLATION")
    print("-"*30)
    for legislation in case_data['legislations']:
        print(f"- {legislation['legislation_name']}")
    print()

    print("REFERENCED JUDGEMENTS")
    print("-"*30)
    for judgement in case_data['referenced_judgements']:
        print(f"- {judgement['neutral_citation']}")

    print("ARGUMENTS")
    print("-"*30)
    for argument in case_data['arguments']:
        print(f"Argument Summary: {argument['summary']}")
        for judgement in argument['judgements_referenced']:
            print(f"- {judgement['neutral_citation']}")
        for legislation in argument['legislations_referenced']:
            print(f"- {legislation['legislation_name']}")


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
        response_format=LawOutput,
        )
        response_choices = response.choices[0].message

        for i in json.loads(response_choices.content).get("case_summary"):
            print_case_details(i)

        return json.loads(response_choices.content).get("case_summary")

    except OpenAIError as e:
        logging.error('An error occurred while trying to retrieve case information - %s', str(e))

if __name__=="__main__":
    api_client = get_client()
    GPT_MODEL = "o3-mini"
    file_names = ['ewhc_kb_2025_287.xml','ewhc_comm_2025_240.xml']
    list_of_cases = get_list_xml_data(filenames=[file_names[0]])
    PROMPT = f"""
    I have a list of court case transcriptions:
    {list_of_cases}

    Please analyse each case and return a summary for each.

    Give me a summary for each of the cases provided. Your response should be in a list of dictionaries containing the following keys:
    - date: date of the approved judgement
    - hearing_dates: a list of dates for all hearings
    - type_of_crime: criminal or civil 
    - description: a short summary of the trial
    - parties : a list of party dictionaries with their names and what role they are -  apellant, defendant, claimant, Also for each party they have some counsels - example William Bennett KC and Ben Hamer (instructed by Brett Wilson LLP) for Dale Vince OBE - William Bennett is a counsel name, KC = Kings Counsel which is a counsel title, Ben Hammer is another Counsel name with no title, Brett Wilson LLP is a chamber name
    - judge : the surname of the judge (e.g., 'Pepperall' or 'Bright', followed by their title (e.g., 'Mr Justice')
    - legislations: a list of the legislation names
    - neutral_citation: the neutral citation number
    - court_name: name of court
    - court_address: the courts address
    - case_number: the value of Case No
    - referenced_judgements: the neutral citations that are referenced are references to other judgements
    - arguments: list of arguments made in the judgement which contains neutral citations(references to other judgements), list of references to legislations and a summary of the argument

  

    This MUST be a json and only be a list of dictionaries
    """

    get_case_summaries(model=GPT_MODEL,client=api_client,prompt=PROMPT)
