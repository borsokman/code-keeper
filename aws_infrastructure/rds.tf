# RDS Instance for Inventory Service
resource "aws_db_instance" "inventory_db" {
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "13" # Matching your original container version
  instance_class       = "db.t4g.micro"
  db_name              = "inventory_db"
  username             = "db_admin"
  password             = var.db_password_inventory
  db_subnet_group_name = aws_db_subnet_group.private.name
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  skip_final_snapshot  = true
}

# RDS Instance for Billing Service
resource "aws_db_instance" "billing_db" {
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "13"
  instance_class       = "db.t4g.micro"
  db_name              = "billing_db"
  username             = "db_admin"
  password             = var.db_password_billing
  db_subnet_group_name = aws_db_subnet_group.private.name
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  skip_final_snapshot  = true
}