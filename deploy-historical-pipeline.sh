source .env
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-2.amazonaws.com
if [ $# -eq 0 ] || [ -z "$1" ]
  then
    docker build --platform linux/arm64 --provenance false -t judgment-reader-historical-pipeline seed_data/.
  else
    docker build --platform linux/arm64 --provenance false -t judgment-reader-historical-pipeline -e DAYS_TO_SEED=$1 seed_data/.
docker tag pigasus-dashbaord:latest ${HISTORICAL_PIPELINE_ECR_URL}:latest
docker push ${HISTORICAL_PIPELINE_ECR_URL}:latest
