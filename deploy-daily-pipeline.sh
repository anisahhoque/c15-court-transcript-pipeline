source .env
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-2.amazonaws.com
docker build --platform linux/arm64 --provenance false -t judgment-reader-pipeline daily_pipeline/.
docker tag judgment-reader-pipeline "${PIPELINE_ECR_URL}:latest"
docker push "${PIPELINE_ECR_URL}:latest"
