variable "project_name" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "alb_security_group_id" {
  type = string
}

variable "blue_instance_id" {
  type = string
}

variable "green_instance_id" {
  type = string
}

variable "active_target" {
  type = string
}

variable "certificate_arn" {
  type = string
}

variable "common_tags" {
  type = map(string)
}

