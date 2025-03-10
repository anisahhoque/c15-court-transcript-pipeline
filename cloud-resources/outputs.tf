output "historical_pipeline_ecr_url" {
  value = aws_ecr_repository.historical_pipeline.repository_url
}

output "pipeline_ecr_url" {
  value = aws_ecr_repository.pipeline.repository_url
}

output "server_ecr_url" {
  value = aws_ecr_repository.server.repository_url
}

output "report_lambda_ecr_url" {
  value = aws_ecr_repository.report_lambda.repository_url
}

output "account_id" {
  value = local.account_id
}
