resource "aws_db_subnet_group" "default" {
  name = "main"
  subnet_ids = [
    aws_subnet.private_a.id, 
    aws_subnet.private_b.id
  ]
}

/*
Currently commented out due to ongoing issue with AWS

resource "aws_security_group" "main_database" {
  name = "judgment-reader-main-database"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port = 5432
    to_port = 5432 
    protocol = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }


  egress {
    from_port = 5432
    to_port = 5432 
    protocol = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
} 
*/

resource "aws_db_instance" "main" {
  allocated_storage = 20
  engine = "postgres"
  engine_version = "17"
  identifier = "judgment-reader"
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
  vpc_security_group_ids = [aws_security_group.master.id]
}

locals {
  main_db_port = aws_db_instance.main.port
}
