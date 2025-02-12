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

resource "aws_vpc" "judgment_project" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "judgment-reader"
  }
}

resource "aws_s3_bucket" "judgment_xml" {
  bucket = "judgment-xml"
  force_destroy = true
}

resource "aws_subnet" "private-a" {
  vpc_id = aws_vpc.judgment_project.id 
  cidr_block = "10.0.3.0/24"
  availability_zone = "eu-west-2a"

  tags = {
    Name = "private-a"
  }
}

resource "aws_subnet" "private-b" {
  vpc_id = aws_vpc.judgment_project.id 
  cidr_block = "10.0.4.0/24"
  availability_zone = "eu-west-2b"

  tags = {
    Name = "private-b"
  }
}

resource "aws_db_subnet_group" "default" {
  name = "main"
  subnet_ids = [
    aws_subnet.private-a.id, 
    aws_subnet.private-b.id
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
}
