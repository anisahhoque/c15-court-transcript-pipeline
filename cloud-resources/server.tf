locals {
  streamlit_server_sg_ports = [
    aws_db_instance.main.port,
    8501
  ]
}

resource "aws_security_group" "streamlit_server" {
  vpc_id = aws_vpc.main.id
  name = "judgment-reader-streamlit-server"

  dynamic "egress" {
    for_each = local.streamlit_server_sg_ports

    content {
      from_port = egress.value
      to_port = egress.value
      protocol = "tcp"
      cidr_blocks = ["10.0.0.0/16"]
    }
  }

  dynamic "ingress" {
    for_each = local.streamlit_server_sg_ports

    content {
      from_port = ingress.value
      to_port = ingress.value
      protocol = "tcp"
      cidr_blocks = ["10.0.0.0/16"]
    }
  }
}

resource "aws_iam_instance_profile" "streamlit_server" {
  name = "judgment-reader-streamlit-server"
  role = aws_iam_role.streamlit_server.name
}

data "aws_iam_policy_document" "streamlit_server_assume" {
  statement {
    effect = "Allow"

    principals {
      type = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "streamlit_server" {
  name = "judgment-reader-streamlit-server"
  assume_role_policy = data.aws_iam_policy_document.streamlit_server_assume.json
}

resource "aws_instance" "streamlit_server" {
  ami = "ami-091f18e98bc129c4e"
  instance_type = "t2.micro"
  associate_public_ip_address = false
  availability_zone = "eu-west-2a"
  iam_instance_profile = "judgment-reader-streamlit-server"
  vpc_security_group_ids = [aws_security_group.streamlit_server.id]
  subnet_id = aws_subnet.private_a.id


  tags = {
    Name = "judgment-reader-streamlit-server"
  }
}
