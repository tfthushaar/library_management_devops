resource "aws_instance" "app" {
  for_each = var.instance_subnet_map

  ami                         = var.ami_id
  instance_type               = var.instance_type
  subnet_id                   = each.value
  key_name                    = var.key_pair_name
  vpc_security_group_ids      = [var.app_security_group_id]
  iam_instance_profile        = var.instance_profile_name
  associate_public_ip_address = true

  root_block_device {
    volume_size = 8
    volume_type = "gp3"
  }

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${each.key}"
      Environment = each.key
      Role        = "library-portal"
    }
  )
}

