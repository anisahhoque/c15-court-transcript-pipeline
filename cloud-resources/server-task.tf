resource "aws_ecs_task_definition" "server" {
  family = "judgment-reader-server"
  network_mode = "host"
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
            value = aws_s3_bucket.judgment_html.id
          },
          {
            name = "CONTACT_LIST_NAME"
            value = aws_sesv2_contact_list.daily_update.contact_list_name
          }
        ]
      logConfiguration = {
          logDriver = "awslogs"
          options = {
            awslogs-group = "judgment-reader-server"
            mode = "non-blocking"
            awslogs-region = "eu-west-2"
            awslogs-stream-prefix = "-"
          }
        }
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
}
