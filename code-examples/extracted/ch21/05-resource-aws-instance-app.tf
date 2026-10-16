resource "aws_instance" "app" {
  ami           = "..."
  instance_type = "t3.micro"

  security_groups = [
    aws_security_group.app.name
  ]
}
