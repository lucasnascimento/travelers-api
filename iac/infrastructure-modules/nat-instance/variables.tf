variable "name" {
  type        = string
  description = "The name"
}
variable "vpc_id" {
  type        = string
  description = "The vpc identifier"
}
variable "public_subnet" {
  type        = string
  description = "The public subnet"
}
variable "private_subnets_cidr_blocks" {
  type        = list(string)
  description = "The private subnets cidrs blocks"
}
variable "private_route_table_ids" {
  type        = list(string)
  description = "The private route table ids"
}
variable "tags" {
  type = map
  description = "The tags"
}
