output "historical_pipeline_ecr_url" {
  value = aws_ecr_repository.historical_pipeline.repository_url
}

output "pipeline_ecr_url" {
  value = aws_ecr_repository.pipeline.repository_url
}

output "server_ecr_url" {
  value = aws_ecr_repository.server.repository_url
}
