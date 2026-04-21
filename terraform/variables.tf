variable "project_name" {
  description = "Project name prefix used for tagging and naming resources."
  type        = string
  default     = "library-devsecops"
}

variable "aws_region" {
  description = "AWS region where resources will be created."
  type        = string
  default     = "ap-south-1"
}

variable "vpc_id" {
  description = "Existing VPC ID where the ALB and EC2 instances will be deployed."
  type        = string
}

variable "public_subnet_ids" {
  description = "Two public subnet IDs used by the ALB and EC2 instances."
  type        = list(string)
}

variable "ami_id" {
  description = "Amazon Linux 2 AMI ID for the EC2 instances."
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type for blue and green instances."
  type        = string
  default     = "t2.micro"
}

variable "key_pair_name" {
  description = "Existing EC2 key pair name for SSH access."
  type        = string
}

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed to SSH into the EC2 instances."
  type        = string
  default     = "0.0.0.0/0"
}

variable "active_target" {
  description = "Target group that should receive live traffic. Allowed values: blue or green."
  type        = string
  default     = "blue"

  validation {
    condition     = contains(["blue", "green"], var.active_target)
    error_message = "active_target must be either 'blue' or 'green'."
  }
}

variable "environment_tags" {
  description = "Common tags applied to all resources."
  type        = map(string)
  default = {
    Owner      = "student"
    Department = "academic-project"
  }
}

variable "certificate_arn" {
  description = "Optional ACM certificate ARN for HTTPS listener. Leave empty to skip HTTPS listener."
  type        = string
  default     = ""
}
