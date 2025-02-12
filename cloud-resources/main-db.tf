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
