resource "aws_ecr_repository" "pipeline" {
  name = "judgment-reader-pipeline"
  image_tag_mutability = "MUTABLE"
  force_delete = true
}

resource "null_resource" "initialise_pipeline_ecr" {
  provisioner "local-exec" {
    command = <<EOT
      aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.eu-west-2.amazonaws.com
      docker build --platform linux/arm64 --provenance false -t pigasus-pipeline .
      docker tag pigasus-pipeline:latest ${aws_ecr_repository.pipeline.repository_url}:latest
      docker push ${aws_ecr_repository.pipeline.repository_url}:latest
    EOT
  }

  depends_on = [aws_ecr_repository.pipeline]
}

locals {
  pipeline_sg_ports = concat(
    var.http_ports,
    [aws_db_instance.main.port]
  )
}

resource "aws_security_group" "pipeline" {
  name = "judgment-reader-pipeline"
  vpc_id = aws_vpc.main.id

  dynamic "ingress" {
    for_each = local.pipeline_sg_ports

    content {
      from_port = ingress.value 
      to_port = ingress.value 
      protocol = "tcp"
    }
  }

  dynamic "egress" {
    for_each = local.pipeline_sg_ports

    content {
      from_port = egress.value 
      to_port = egress.value
      protocol = "tcp"
    }
  }
}

resource "aws_ecs_task_definition" "pipeline" {
  family = "judgment-reader-pipeline"
  requires_compatibilities = ["FARGATE"]
  network_mode = "awsvpc"
  cpu = 256
  memory = 512
  execution_role_arn = "arn:aws:iam::129033205317:role/ecsTaskExecutionRole"
  container_definitions = jsonencode(
    {
      name = "judgment-reader-pipeline"
      image = "${aws_ecr_repository.pipeline.repository_url}:latest"
      cpu = 256 
      memory = 512
      essential = true 
      environment = [
        {
          name = "DB_NAME"
          value = var.db_name
        },
        {
          name = "DB_USER"
          value = var.db_user
        },
        {
          name = "DB_PASSWORD"
          value = var.db_password
        },
        {
          name = "DB_HOST"
          value = aws_db_instance.main.address
        },
        {
          name = "DB_PORT"
          value = aws_db_instance.main.port
        },
        {
          name = "ACCESS_KEY"
          value = var.access_key
        },
        {
          name = "SECRET_KEY"
          value = var.secret_key
        },
        {
          name = "BUCKET_NAME"
          value = aws_s3_bucket.judgment_xml.id
        }
      ]
    portMappings = [
        {
          containerPort = 80
          hostPort = 80
        },
        {
          containerPort = 443
          hostPort = 443
        },
        {
          containerPort = aws_db_instance.main.port
          hostPort = aws_db_instance.main.port
        }
      ]
    }
  )

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture = "X86_64"
  }
}
