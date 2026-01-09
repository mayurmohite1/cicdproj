# Terraform variables for N. Virginia (us-east-1) region
# VPC and subnet configuration for EKS deployment

vpc_cidr_block = "10.0.0.0/16"

private_subnet_cidr_blocks = [
  "10.0.1.0/24", # us-east-1a
  "10.0.2.0/24", # us-east-1b
  "10.0.3.0/24"  # us-east-1c
]

public_subnet_cidr_blocks = [
  "10.0.101.0/24", # us-east-1a
  "10.0.102.0/24", # us-east-1b
  "10.0.103.0/24"  # us-east-1c
]
