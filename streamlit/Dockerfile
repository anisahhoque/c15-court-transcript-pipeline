FROM python:latest

RUN mkdir streamlit
RUN mkdir streamlit/pages

WORKDIR ~/streamlit

COPY Home.py .
COPY components.py .
COPY dashboard_functions.py .
COPY data_source.py .
COPY requirements.txt .
COPY pages/* ./pages

RUN pip install -r requirements.txt

CMD ["streamlit", "run", "Home.py", "--server.port", "80"]

