"""This file extracts data from xmls using OpenAI API"""
import json
from os import environ as ENV
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

class Party(BaseModel):
    party_name: str
    party_role: str

class Judge(BaseModel):
    judge_name: str
    jurisdiction_name: str
    judge_title: str

class Legislation(BaseModel):
    legislation_name: str

class CaseOutput(BaseModel):
    type_of_crime: str
    description: str
    parties: list[Party]
    judge: list[Judge]
    legislations: list[Legislation]
    neutral_citation: str
    court_name: str
    court_address: str
    case_number: str
    

class LawOutput(BaseModel):
    case_summary: list[CaseOutput]

def print_case_details(case_data: dict):
    """
    Formats and prints case data in a clean, readable format
    Args:
        case_data: Dictionary containing the case information
    """
    print("\n" + "="*50)
    print(f"CASE #{case_data['case_number']}")
    print("="*50 + "\n")

    print("COURT DETAILS")
    print("-"*30)
    print(f"Court: {case_data['court_name']}")
    print(f"Address: {case_data['court_address']}")

    print("CASE OVERVIEW")
    print("-"*30)
    print(f"Citation: {case_data['neutral_citation']}\n")
    print(f"Type of Crime: {case_data['type_of_crime']}")
    print(f"Description: {case_data['description']}\n")

    print("PARTIES INVOLVED")
    print("-"*30)
    for party in case_data['parties']:
        print(f"Name: {party['party_name']}")
        print(f"Role: {party['party_role']}")
        print()


    print("JUDGES")
    print("-"*30)
    for judge in case_data['judge']:
        print(f"Name: {judge['judge_name']}")
        print(f"Title: {judge['judge_title']}")
        print(f"Jurisdiction: {judge['jurisdiction_name']}")
        print()

    print("RELEVANT LEGISLATION")
    print("-"*30)
    for legislation in case_data['legislations']:
        print(f"- {legislation['legislation_name']}")
    print()
if __name__=="__main__":

    load_dotenv()
    gpt_model = "o3-mini"
    list_of_cases = []
    file_names = ['ewhc_kb_2025_287.xml','ewhc_comm_2025_240.xml']
    for file in file_names:
        with open(file, 'r') as file:
            list_of_cases.append(file.read())

    prompt = f"""
    I have a list of court case transcriptions:
    {list_of_cases}

    Please analyse each case and return a summary for each.

    Give me a summary for each of the cases provided. Your response should be in a list of dictionaries containing the following keys:
   
    - type_of_crime: criminal or civil 
    - description: a short summary of the trial
    - parties : a list of party dictionaries with their names and whether they are an apellant or respondent
    - judge : judge: the surname of the judge (e.g., 'Pepperall' or 'Bright', followed by their title (e.g., 'Mr Justice'), their jurisdiction from the following England and Wales, Nothern Ireland, Scotland
    - legislations: a list of the legislation names
    - neutral_citation: the neutral citation number
    - court_name: name of court
    - court_address: the courts address
    - case_number: the value of Case No

  

    This MUST be a json and only be a list of dictionaries
    """
    client = OpenAI(
    api_key=ENV.get("OPENAI_API_KEY"),
    timeout=10.0,
    )
    response = client.with_options(timeout=60.0).beta.chat.completions.parse(
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    model=gpt_model,
    response_format=LawOutput,
    )
    response.choices
    response_choices = response.choices[0].message
    for i in json.loads(response_choices.content).get("case_summary"):
        print(print_case_details(i))
