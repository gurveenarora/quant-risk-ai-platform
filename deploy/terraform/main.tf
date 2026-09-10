# Terraform Infrastructure as Code (IaC) configuration for Cloud Deployment

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "us-east-1"
}

resource "aws_ecs_cluster" "quant_cluster" {
  name = "quant-risk-ai-cluster"
}

resource "aws_elasticache_cluster" "redis_cache" {
  cluster_id           = "quant-redis-cache"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.quant_cluster.name
}
