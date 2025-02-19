source .env
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-2.amazonaws.com
docker build --platform linux/arm64 --provenance false -t judgment-reader-server streamlit/.
docker tag pigasus-dashbaord:latest ${SERVER_ECR_REPOSITORY_URL}:latest
docker push ${SERVER_ECR_REPOSITORY_URL}:latest
aws ecs update-service --region eu-west-2 --cluster judgment-reader --service judgment-reader-server --task-definition judgment-reader-server:latest --force-new-deployment
