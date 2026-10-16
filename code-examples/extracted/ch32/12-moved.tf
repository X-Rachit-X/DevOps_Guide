moved {
  from = aws_s3_bucket.assets
  to   = module.storage.aws_s3_bucket.assets
}
