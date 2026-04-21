output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer."
  value       = module.alb.alb_dns_name
}

output "listener_arn" {
  description = "ALB HTTP listener ARN used by Jenkins to switch blue-green traffic."
  value       = module.alb.listener_arn
}

output "blue_target_group_arn" {
  description = "ARN of the blue target group."
  value       = module.alb.target_group_arns["blue"]
}

output "green_target_group_arn" {
  description = "ARN of the green target group."
  value       = module.alb.target_group_arns["green"]
}

output "blue_instance_public_ip" {
  description = "Public IP address of the blue instance."
  value       = module.compute.instance_public_ips["blue"]
}

output "green_instance_public_ip" {
  description = "Public IP address of the green instance."
  value       = module.compute.instance_public_ips["green"]
}

output "cloudwatch_log_group_name" {
  description = "CloudWatch log group used by Apache and Gunicorn logs."
  value       = module.observability.log_group_name
}

