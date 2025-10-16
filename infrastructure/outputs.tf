output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "private_subnets" {
  description = "List of IDs of private subnets"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of IDs of public subnets"
  value       = module.vpc.public_subnets
}

output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.postgres.endpoint
  sensitive   = true
}

output "database_port" {
  description = "RDS instance port"
  value       = aws_db_instance.postgres.port
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
}

output "redis_port" {
  description = "ElastiCache Redis port"
  value       = aws_elasticache_replication_group.redis.port
}

output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the load balancer"
  value       = aws_lb.main.zone_id
}

output "ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.main.arn
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.backend.name
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.backend.repository_url
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.data.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.data.arn
}

output "application_url" {
  description = "URL of the application"
  value       = "http://${aws_lb.main.dns_name}"
}

output "grafana_url" {
  description = "URL of Grafana dashboard"
  value       = "http://${aws_lb.main.dns_name}:3000"
}

output "prometheus_url" {
  description = "URL of Prometheus"
  value       = "http://${aws_lb.main.dns_name}:9090"
}

output "flower_url" {
  description = "URL of Flower (Celery monitoring)"
  value       = "http://${aws_lb.main.dns_name}:5555"
}

output "security_groups" {
  description = "Security group IDs"
  value = {
    alb   = aws_security_group.alb.id
    ecs   = aws_security_group.ecs.id
    rds   = aws_security_group.rds.id
    redis = aws_security_group.redis.id
  }
}

output "iam_roles" {
  description = "IAM role ARNs"
  value = {
    ecs_execution_role = aws_iam_role.ecs_execution_role.arn
    ecs_task_role     = aws_iam_role.ecs_task_role.arn
  }
}

output "secrets_manager_arns" {
  description = "Secrets Manager secret ARNs"
  value = {
    apollo_api_key = aws_secretsmanager_secret.apollo_api_key.arn
    openai_api_key = aws_secretsmanager_secret.openai_api_key.arn
    claude_api_key = aws_secretsmanager_secret.claude_api_key.arn
  }
  sensitive = true
}
