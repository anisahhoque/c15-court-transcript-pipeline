resource "aws_ecr_repository" "server" {
  name = "judgment-reader-server"
  image_tag_mutability = "MUTABLE"
  force_delete = true
}

resource "null_resource" "server_ecr_dummy_image" {
  provisioner "local-exec" {
    command = <<EOT
      aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.eu-west-2.amazonaws.com
      docker pull public.ecr.aws/ecs-sample-image/amazon-ecs-sample:latest
      docker build --platform linux/arm64 --provenance false -t judgment-reader-server .
      docker tag public.ecr.aws/ecs-sample-image/amazon-ecs-sample:latest ${aws_ecr_repository.server.repository_url}:latest
      docker push ${aws_ecr_repository.server.repository_url}:latest
    EOT
  }
}

