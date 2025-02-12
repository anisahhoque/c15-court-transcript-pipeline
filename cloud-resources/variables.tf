variable "access_key" {
  type = string
}

variable "secret_key" {
  type = string
}

variable "db_name" {
  type = string
}

variable "db_user" {
  type = string
}

variable "db_password" {
  type = string
}

variable "pipeline_sg_ports" {
  type = list(number)
  default = [
    80,
    443
  ]
}
