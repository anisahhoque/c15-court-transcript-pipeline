resource "aws_s3_bucket" "judgment_xml" {
  bucket = "judgment-xml"
  force_destroy = true
}
