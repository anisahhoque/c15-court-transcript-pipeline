resource "aws_cloudwatch_log_group" "server" {
  name = "judgment-reader-server"
  retention_in_days = 7
}

/*
Currently commented out due to ongoing issue with AWS
resource "aws_security_group" "server_alb" {
  name = "judgment-reader-server-lb"
  vpc_id = aws_vpc.main.id

  dynamic "ingress" {
    for_each = var.http_ports

    content {
      from_port = ingress.value
      to_port = ingress.value
      protocol = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  dynamic "egress" {
    for_each = var.http_ports

    content {
      from_port = egress.value
      to_port = egress.value
      protocol = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
}
*/

resource "aws_alb" "server" {
  name = "judgment-reader-server"
  internal = false
  load_balancer_type = "application"
  security_groups = [aws_security_group.master.id]
  subnets = [aws_subnet.public_a.id, aws_subnet.public_b.id]

  enable_deletion_protection = false

  depends_on = [aws_alb_target_group.server]
}

resource "aws_alb_listener" "server" {
  load_balancer_arn = aws_alb.server.arn
  port = 80
  protocol = "HTTP"
  default_action {
    type = "forward"
    target_group_arn = aws_alb_target_group.server.arn
  }

  depends_on = [aws_alb_target_group.server]
}

resource "aws_alb_target_group" "server" {
  name = "judment-reader-server-service"
  target_type = "instance"
  port = 80
  protocol = "HTTP"
  vpc_id = aws_vpc.main.id
}

resource "aws_ecs_service" "server" {
  name = "judgment-reader-server"
  cluster = aws_ecs_cluster.main.id
  launch_type = "EC2"
  task_definition = aws_ecs_task_definition.server.id 
  force_delete = true 
  desired_count = 1 
  deployment_minimum_healthy_percent = 0 
  load_balancer {
    target_group_arn = aws_alb_target_group.server.arn 
    container_name = "judgment-reader-server"
    container_port = 80
  }
}
