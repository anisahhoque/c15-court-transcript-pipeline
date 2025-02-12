terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-west-2"
  access_key = var.access_key
  secret_key = var.secret_key
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "judgment-reader"
  }
}

resource "aws_s3_bucket" "judgment_xml" {
  bucket = "judgment-xml"
  force_destroy = true
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "judgement-reader"
  }
}

resource "aws_subnet" "public_a" {
  vpc_id = aws_vpc.main.id 
  cidr_block = "10.0.1.0/24"
  availability_zone = "eu-west-2a"
  map_public_ip_on_launch = true

  tags = {
    Name = "public-a"
  }
}

resource "aws_subnet" "public_b" {
  vpc_id = aws_vpc.main.id 
  cidr_block = "10.0.2.0/24"
  availability_zone = "eu-west-2b"
  map_public_ip_on_launch = true

  tags = {
    Name = "public-b"
  }
}

resource "aws_subnet" "private_a" {
  vpc_id = aws_vpc.main.id 
  cidr_block = "10.0.3.0/24"
  availability_zone = "eu-west-2a"
  map_public_ip_on_launch = false

  tags = {
    Name = "private-a"
  }
}

resource "aws_subnet" "private_b" {
  vpc_id = aws_vpc.main.id 
  cidr_block = "10.0.4.0/24"
  availability_zone = "eu-west-2b"
  map_public_ip_on_launch = false

  tags = {
    Name = "private-b"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id 
  }

  tags = {
    Name = "judgment-project-public"
  }
}

resource "aws_route_table_association" "public_a" {
  subnet_id = aws_subnet.public_a.id 
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_b" {
  subnet_id = aws_subnet.public_b.id 
  route_table_id = aws_route_table.public.id
}

resource "aws_db_subnet_group" "default" {
  name = "main"
  subnet_ids = [
    aws_subnet.private_a.id, 
    aws_subnet.private_b.id
  ]
}

resource "aws_db_instance" "main" {
  allocated_storage = 20
  engine = "postgres"
  engine_version = "17"
  identifier = "c15-judgment-reader"
  instance_class = "db.t4g.micro"
  storage_encrypted = false
  publicly_accessible = false 
  delete_automated_backups = true 
  skip_final_snapshot = true 
  db_name = var.db_name
  username = var.db_user
  password = var.db_password
  apply_immediately = true 
  multi_az = false
  db_subnet_group_name = aws_db_subnet_group.default.name
  deletion_protection = false
}
