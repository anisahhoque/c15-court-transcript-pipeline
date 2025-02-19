# Judgment Reader Infrastructure

## Requirements
- An AWS account with a key configured
- Terraform
- Docker daemon

## Deployment
1. You must have a file in this directory named `terraform.tfvars` configured in the following manner:
```HCL
access_key  = "<string: your AWS access key>"
secret_key  = "<string: your AWS secret key>"
db_name     = "<string: an arbitrary string to name your database>"
db_user     = "<string: an arbitrary string to name your database user>"
db_password = "<string: an arbitrary string to set as your database password>"
openai_key  = "<string: your OpenAI API key>"
```

2. You **must** have the Docker daemon running. See below for details.

3. Run 
```bash
terraform init
```

4. Run 
```HCL
terraform apply
```

5. You will get two outputs which are needed to configure the actual applications:
```
pipeline_ecr_url = <the url for your pipeline ECR repository>
server_ecr_url   = <the url for your server ECR repository>
```

## Dev notes
### Docker 
The Docker daemon is necessary in order to seed the ECR repositories. In each of respective files which create ECR repositories, they are populated using `null_resource` provisioners. This is necessary as if the repositories are not populated the task definitions for the various apps cannot be created. The Docker daemon is required in order to build the images, tag them, and then deploy them to ECR.
