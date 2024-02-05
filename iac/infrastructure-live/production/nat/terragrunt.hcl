include "root" {
  path = find_in_parent_folders()
}

terraform {
  source = "../../../infrastructure-modules/nat-instance//"
}


inputs = {
  name                        = "production-nat-instance"
  vpc_id                      = "vpc-0f79a5c362cdc16c9"
  public_subnet               = "subnet-02041aa099bf93b11"
  private_subnets_cidr_blocks = ["10.0.1.0/24","10.0.2.0/24","10.0.3.0/24"]
  private_route_table_ids     = ["rtb-0cf2ecd0972b96887"]
  tags = {
    Terraform = "true"
    Environment = "production"
  }
}
