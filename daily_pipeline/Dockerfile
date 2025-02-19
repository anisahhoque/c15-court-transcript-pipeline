FROM python:latest

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

COPY daily_extract.py .
COPY daily_parse_xml.py .
COPY daily_prompt_engineering.py .
COPY daily_transform.py .
COPY daily_load.py .
COPY daily_pipeline.py .

CMD [ "python", "daily_pipeline.py"]