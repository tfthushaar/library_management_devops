output "alb_dns_name" {
  value = aws_lb.this.dns_name
}

output "alb_arn_suffix" {
  value = aws_lb.this.arn_suffix
}

output "listener_arn" {
  value = aws_lb_listener.http.arn
}

output "target_group_arns" {
  value = {
    blue  = aws_lb_target_group.blue.arn
    green = aws_lb_target_group.green.arn
  }
}

output "target_group_arn_suffixes" {
  value = {
    blue  = aws_lb_target_group.blue.arn_suffix
    green = aws_lb_target_group.green.arn_suffix
  }
}

