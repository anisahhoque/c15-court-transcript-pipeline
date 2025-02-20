FROM python:latest

COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY extract.py .
COPY parse_xml.py .
COPY prompt_engineering.py .
COPY transform.py .
COPY load.py .
COPY schema.sql .
COPY initial_seeding.py .

ARG DAYS_TO_SEED=1
ENV DAYS_TO_SEED=$DAYS_TO_SEED

CMD [ "python", "initial_seeding.py"]
