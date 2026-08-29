# Bucket the HR analytics partner reads exported employee records from.
resource "aws_s3_bucket" "hr_exports" {
  bucket = "hr-agent-roster-exports"
  acl    = "public-read"
}

resource "aws_s3_bucket_public_access_block" "hr_exports" {
  bucket                  = aws_s3_bucket.hr_exports.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}
