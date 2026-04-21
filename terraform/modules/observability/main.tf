resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/${var.project_name}/apache"
  retention_in_days = 14

  tags = merge(var.common_tags, { Name = "${var.project_name}-log-group" })
}

resource "aws_cloudwatch_dashboard" "project_dashboard" {
  dashboard_name = "${var.project_name}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title   = "EC2 CPU Utilization"
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          metrics = [for instance_id in var.instance_ids : ["AWS/EC2", "CPUUtilization", "InstanceId", instance_id]]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "ALB Request Count"
          view   = "timeSeries"
          region = var.aws_region
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", var.alb_arn_suffix]
          ]
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "Healthy Hosts"
          view   = "timeSeries"
          region = var.aws_region
          metrics = [
            ["AWS/ApplicationELB", "HealthyHostCount", "TargetGroup", var.blue_tg_suffix, "LoadBalancer", var.alb_arn_suffix],
            ["AWS/ApplicationELB", "HealthyHostCount", "TargetGroup", var.green_tg_suffix, "LoadBalancer", var.alb_arn_suffix]
          ]
        }
      }
    ]
  })
}

