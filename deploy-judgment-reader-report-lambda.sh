source .env
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-2.amazonaws.com
docker build --platform linux/arm64 --provenance false -t judgment-reader-report-lambda judgment-reader-report-lambda/.
docker tag judgment-reader-report-lambda ${REPORT_LAMBDA_ECR_URL}:latest
docker push ${REPORT_LAMBDA_ECR_URL}:latest
aws lambda update-function-code \
  --function-name judgment-reader-report --image-uri ${REPORT_LAMBDA_ECR_URL}:latest
