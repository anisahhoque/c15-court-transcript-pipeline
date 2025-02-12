resource "aws_ecr_repository" "pipeline" {
  name = "daily-judgment-pipeline"
  image_tag_mutability = "MUTABLE"
  force_delete = true

  provisioner "local-exec" {
    command = <<EOT
      aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.eu-west-2.amazonaws.com
      docker build --platform linux/arm64 --provenance false -t pigasus-pipeline .
      docker tag pigasus-pipeline:latest ${aws_ecr_repository.pipeline.repository_url}:latest
      docker push ${aws_ecr_repository.pipeline.repository_url}:latest    
    EOT
  }
}

resource "aws_security_group" "pipeline" {
  name = "judgment-reader-pipeline"
  vpc_id = aws_vpc.main.id

  dynamic "ingress" {
    for_each = var.pipeline_sg_ports

    content {
      from_port = ingress.value 
      to_port = ingress.value 
      protocol = "tcp"
    }
  }

  dynamic "egress" {
    for_each = var.pipeline_sg_ports 

    content {
      from_port = egress.value 
      to_port = egress.value
      protocol = "tcp"
    }
  }
}
