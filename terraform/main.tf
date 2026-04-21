locals {
  common_tags = merge(
    {
      Project = var.project_name
    },
    var.environment_tags
  )

  instance_subnet_map = {
    blue  = var.public_subnet_ids[0]
    green = var.public_subnet_ids[1]
  }
}

module "security" {
  source = "./modules/security"

  project_name      = var.project_name
  vpc_id            = var.vpc_id
  allowed_ssh_cidr  = var.allowed_ssh_cidr
  common_tags       = local.common_tags
}

module "iam" {
  source = "./modules/iam"

  project_name = var.project_name
  common_tags  = local.common_tags
}

module "compute" {
  source = "./modules/compute"

  project_name          = var.project_name
  ami_id                = var.ami_id
  instance_type         = var.instance_type
  key_pair_name         = var.key_pair_name
  app_security_group_id = module.security.app_security_group_id
  instance_profile_name = module.iam.instance_profile_name
  instance_subnet_map   = local.instance_subnet_map
  common_tags           = local.common_tags
}

module "alb" {
  source = "./modules/alb"

  project_name           = var.project_name
  vpc_id                 = var.vpc_id
  public_subnet_ids      = var.public_subnet_ids
  alb_security_group_id  = module.security.alb_security_group_id
  blue_instance_id       = module.compute.instance_ids["blue"]
  green_instance_id      = module.compute.instance_ids["green"]
  active_target          = var.active_target
  certificate_arn        = var.certificate_arn
  common_tags            = local.common_tags
}

module "observability" {
  source = "./modules/observability"

  project_name   = var.project_name
  aws_region     = var.aws_region
  instance_ids   = values(module.compute.instance_ids)
  alb_arn_suffix = module.alb.alb_arn_suffix
  blue_tg_suffix = module.alb.target_group_arn_suffixes["blue"]
  green_tg_suffix = module.alb.target_group_arn_suffixes["green"]
  common_tags    = local.common_tags
}

