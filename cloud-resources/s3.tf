resource "aws_s3_bucket" "judgment_html" {
  bucket = "judgment-html"
  force_destroy = true
}
