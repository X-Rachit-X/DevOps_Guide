resource "aws_instance" "app" {
  ami           = "ami-example"
  instance_type = "t3.micro"
}
