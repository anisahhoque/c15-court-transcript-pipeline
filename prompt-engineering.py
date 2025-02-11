from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
import json
from os import environ as ENV


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
    case_number: int
    

class LawOutput(BaseModel):
    case_summary: list[CaseOutput]

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
    - judge : the name of the judge, and their title, their jurisdiction
    - legislations: a list of the legislation names
    - neutral_citation: the neutral citation number
    - court_name: name of court
    - court_address: the courts address
    - case_number: the number of the case

  


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
    print(json.loads(response_choices.content).get("case_summary"))