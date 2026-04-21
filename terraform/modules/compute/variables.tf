variable "project_name" {
  type = string
}

variable "ami_id" {
  type = string
}

variable "instance_type" {
  type = string
}

variable "key_pair_name" {
  type = string
}

variable "app_security_group_id" {
  type = string
}

variable "instance_profile_name" {
  type = string
}

variable "instance_subnet_map" {
  type = map(string)
}

variable "common_tags" {
  type = map(string)
}

