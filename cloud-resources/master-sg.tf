resource "aws_security_group" "master" {
  name = "judgment-reader-master"
  vpc_id = aws_vpc.main.id
}

resource "aws_vpc_security_group_egress_rule" "allow_all" {
  security_group_id = aws_security_group.master.id
  cidr_ipv4 = "0.0.0.0/0"
  from_port = 0 
  to_port = 65535
  ip_protocol = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = aws_security_group.master.id
  cidr_ipv4 = "0.0.0.0/0"
  from_port = 80
  to_port = 80
  ip_protocol = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "https" {
  security_group_id = aws_security_group.master.id
  cidr_ipv4 = "0.0.0.0/0"
  from_port = 443
  to_port = 443
  ip_protocol = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "postgres" {
  security_group_id = aws_security_group.master.id
  cidr_ipv4 = "0.0.0.0/0"
  from_port = 5432
  to_port = 5432
  ip_protocol = "tcp"
}
