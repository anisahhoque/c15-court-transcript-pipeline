locals {
  server_sg_ports = concat(
    var.http_ports,
    [aws_db_instance.main.port]
  )
}

resource "aws_security_group" "server" {
  name = "judgment-reader-server"
  vpc_id = aws_vpc.main.id

  dynamic "ingress" {
    for_each = local.server_sg_ports

    content {
      from_port = ingress.value 
      to_port = ingress.value 
      protocol = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  dynamic "egress" {
    for_each = local.server_sg_ports

    content {
      from_port = egress.value 
      to_port = egress.value
      protocol = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
}

resource "aws_ecs_task_definition" "server" {
  family = "judgment-reader-server"
  requires_compatibilities = ["FARGATE"]
  network_mode = "awsvpc"
  cpu = 256
  memory = 512
  execution_role_arn = "arn:aws:iam::129033205317:role/ecsTaskExecutionRole"
  container_definitions = jsonencode(
    [
      {
        name = "judgment-reader-server"
        image = "${aws_ecr_repository.server.repository_url}:latest"
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
