source .env
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-2.amazonaws.com
if [ $# -eq 0 ] || [ -z "$1" ]; then
  docker build --platform linux/amd64 --provenance false -t judgment-reader-historical-pipeline seed_data/.
else
  docker build --platform linux/amd64 --provenance false -t judgment-reader-historical-pipeline --build-arg DAYS_TO_SEED=$1 seed_data/.
fi
docker tag judgment-reader-historical-pipeline ${HISTORICAL_PIPELINE_ECR_URL}:latest
docker push ${HISTORICAL_PIPELINE_ECR_URL}:latest
aws ecs run-task \
  --cluster judgment-reader \
  --count 1 \
  --launch-type FARGATE \
  --network-configuration '{ "awsvpcConfiguration": { "assignPublicIp":"ENABLED", "securityGroups": ["sg-01f8ba6f3d1b60ccb"], "subnets": ["subnet-0b45c4714518242d6","subnet-026a47b92b762e0eb"]}}' \
  --task-definition arn:aws:ecs:eu-west-2:${AWS_ACCOUNT_ID}:task-definition/judgment-reader-historical-pipeline
