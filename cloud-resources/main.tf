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

resource "aws_vpc" "judgement_project" {}

resource "aws_s3_bucket" "judgement_xml" {
  bucket = "judgement_xml"
  force_destroy = true
}
