output "pipeline_ecr_url" {
  value = aws_ecr_repository.pipeline.repository_url
}

output "server_ecr_url" {
  value = aws_ecr_repository.server.repository_url
}

output "historical_pipeline_ecr_url" {
  value = aws_ecr_repository.hsitorical_pipeline.repository_url
}
