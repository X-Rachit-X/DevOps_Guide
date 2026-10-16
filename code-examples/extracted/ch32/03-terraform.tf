terraform {
  backend "s3" {
    bucket = "company-terraform-state"
    key    = "production/network/terraform.tfstate"
    region = "..."
  }
}
