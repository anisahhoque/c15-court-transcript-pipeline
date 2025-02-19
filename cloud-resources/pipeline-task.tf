resource "aws_ecr_repository" "pipeline" {
  name = "judgment-reader-pipeline"
  image_tag_mutability = "MUTABLE"
  force_delete = true
}

resource "null_resource" "initialise_pipeline_ecr" {
  provisioner "local-exec" {
    command = <<EOT
      aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.eu-west-2.amazonaws.com
      docker pull hello-world
      docker tag hello-world ${aws_ecr_repository.pipeline.repository_url}:latest
      docker push ${aws_ecr_repository.pipeline.repository_url}:latest
    EOT
  }
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
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  dynamic "egress" {
    for_each = local.pipeline_sg_ports

    content {
      from_port = egress.value 
      to_port = egress.value
      protocol = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
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
    [
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
            value = tostring(aws_db_instance.main.port)
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
          },
          {
            name = "OPENAI_KEY"
            value = var.openai_key
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
    ]
  )

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture = "X86_64"
  }
}

data "aws_iam_policy_document" "pipeline_scheduler_assume" {
  statement {
    effect = "Allow"

    principals {
      type = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "pipeline_scheduler_permissions" {
  statement {
    effect = "Allow"
    actions = ["ecs:RunTask"]
    resources = [aws_ecs_task_definition.pipeline.arn]
  }

  statement {
    effect = "Allow"
    actions = ["iam:PassRole"]
    resources = [
      "arn:aws:iam::129033205317:role/ecsTaskExecutionRole"
    ]
  }
}

resource "aws_iam_role" "pipeline_scheduler" {
  name = "judgment-reader-pipeline"
  assume_role_policy = data.aws_iam_policy_document.pipeline_scheduler_assume.json
}

resource "aws_iam_role_policy" "pipeline_scheduler" {
  name = "judgment-reader-pipeline"
  role = aws_iam_role.pipeline_scheduler.id 
  policy = data.aws_iam_policy_document.pipeline_scheduler_permissions.json
}

resource "aws_scheduler_schedule" "pipeline" {
  name = "judgment-reader-pipeline"
  schedule_expression = "cron(1 0 * * ?)"

  flexible_time_window {
    mode = "FLEXIBLE"
    maximum_window_in_minutes = 60
  }

  target {
    arn = aws_ecs_cluster.main.arn
    role_arn = aws_iam_role.pipeline_scheduler.arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.pipeline.arn
      enable_execute_command = true
      launch_type = "FARGATE"
      task_count = 1

      network_configuration {
        assign_public_ip = true
        security_groups = [aws_security_group.pipeline.id]
        subnets = [
          aws_subnet.public_a.id,
          aws_subnet.public_b.id
        ]
      }
    }
  }
}

