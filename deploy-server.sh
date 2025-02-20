source .env
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-2.amazonaws.com
docker build --platform linux/amd64 --provenance false -t judgment-reader-server streamlit/.
docker tag judgment-reader-server ${SERVER_ECR_URL}:latest
docker push ${SERVER_ECR_URL}:latest
aws ecs list-task-definitions --family-prefix judgment-reader-server --region eu-west-2 |
  aws ecs update-service --region eu-west-2 --cluster judgment-reader --service judgment-reader-server --force-new-deployment
