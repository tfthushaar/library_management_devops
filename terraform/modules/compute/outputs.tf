output "instance_ids" {
  value = { for key, instance in aws_instance.app : key => instance.id }
}

output "instance_public_ips" {
  value = { for key, instance in aws_instance.app : key => instance.public_ip }
}

