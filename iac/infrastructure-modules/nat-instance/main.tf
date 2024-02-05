module "nat" {
  source = "int128/nat-instance/aws"

  name                        = var.name
  vpc_id                      = var.vpc_id
  public_subnet               = var.public_subnet
  private_subnets_cidr_blocks = var.private_subnets_cidr_blocks
  private_route_table_ids     = var.private_route_table_ids
}

resource "aws_eip" "nat" {
  network_interface = module.nat.eni_id
  tags = {
    "Name" = "nat-instance-main"
  }
}
