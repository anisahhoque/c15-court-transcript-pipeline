FROM --platform=linux/amd64 python:latest AS build

ENV DAYS_TO_SEED=30

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

COPY extract.py .
COPY parse_xml.py .
COPY prompt_engineering.py .
COPY transform.py .
COPY load.py .
COPY schema.sql . 
COPY initial_seeding.py .

CMD [ "python", "initial_seeding.py"]
