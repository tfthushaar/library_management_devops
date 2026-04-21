variable "project_name" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "allowed_ssh_cidr" {
  type = string
}

variable "common_tags" {
  type = map(string)
}

