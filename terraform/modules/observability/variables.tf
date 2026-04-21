variable "project_name" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "instance_ids" {
  type = list(string)
}

variable "alb_arn_suffix" {
  type = string
}

variable "blue_tg_suffix" {
  type = string
}

variable "green_tg_suffix" {
  type = string
}

variable "common_tags" {
  type = map(string)
}

