locals {
  server_sg_ports = concat([
      aws_db_instance.main.port,
      8501,
      22
    ],
    var.http_ports
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

data "aws_iam_policy_document" "server_instance_assume" {
  statement {
    effect = "Allow"

    principals {
      type = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "server" {
  name = "judgment-reader-streamlit-server"
  assume_role_policy = data.aws_iam_policy_document.server_instance_assume.json
}

resource "aws_iam_role_policy_attachment" "server_basic" {
  role       = aws_iam_role.server.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
  }

resource "aws_iam_role_policy_attachment" "server_registry" {
  role       = aws_iam_role.server.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
}

resource "aws_iam_instance_profile" "server" {
  name_prefix = "judgment-reader-server"
  path = "/ecs/instance/"
  role = aws_iam_role.server.name
}

resource "aws_launch_template" "server" {
  name_prefix = "judgment-reader-server"
  image_id = "ami-000306e6f42537aac"
  instance_type = "t2.small"
  vpc_security_group_ids = [aws_security_group.server.id]

  iam_instance_profile {
    arn = aws_iam_instance_profile.server.arn
  }

  monitoring {
    enabled = true
  }

  user_data = base64encode(<<-EOF
    #!/bin/bash
    echo ECS_CLUSTER=${aws_ecs_cluster.main.name} >> etc/ecs/ecs.config
  EOF
  )
}

resource "aws_autoscaling_group" "server" {
  name = "judgment-reader-server"
  max_size = 1
  min_size = 1
  desired_capacity = 1
  force_delete = true
  target_group_arns = [aws_alb_target_group.server.arn]
  vpc_zone_identifier = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id
  ]

  launch_template {
    id = aws_launch_template.server.id
    version = "$Latest"
  }

  tag {
    key = "AmazonECSManaged"
    value = ""
    propagate_at_launch = true
  }
}

resource "aws_ecs_capacity_provider" "server" {
  name = "judgment-reader"

  auto_scaling_group_provider {
    auto_scaling_group_arn = aws_autoscaling_group.server.arn
    managed_termination_protection = "DISABLED"

    managed_scaling {
      maximum_scaling_step_size = 1
      minimum_scaling_step_size = 1
      status = "ENABLED"
      target_capacity = 100
    }
  }
}

resource "aws_ecs_cluster_capacity_providers" "server" {
  cluster_name = aws_ecs_cluster.main.name
  capacity_providers = [aws_ecs_capacity_provider.server.name]

  default_capacity_provider_strategy {
    capacity_provider = aws_ecs_capacity_provider.server.name
    base = 1
    weight = 100
  }
}
