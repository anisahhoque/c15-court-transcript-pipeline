FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY judgment_reader_report_lambda.py .

ENV AWS_LAMBDA_FUNCTION_HANDLER=judgment_reader_report_lambda.handler

CMD ["judgment_reader_report_lambda.handler"]