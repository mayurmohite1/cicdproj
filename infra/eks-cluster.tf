module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "21.6.1"

  name                   = "myapp-eks-cluster"
  kubernetes_version     = "1.31"
  endpoint_public_access = true

  # Configure the VPC and Subnets -->
  subnet_ids = module.myapp-vpc.private_subnets
  vpc_id     = module.myapp-vpc.vpc_id

  addons = {
    vpc-cni    = { most_recent = true }
    kube-proxy = { most_recent = true }
    coredns    = { most_recent = true }
  }

  # Configure Node Groups (worker nodes)
  eks_managed_node_groups = {
    dev = {
      min_size     = 1
      max_size     = 3
      desired_size = 3 # Start with 1 node to avoid capacity issues

      instance_types = ["t3.medium"] # Use t3.small instead of t3.micro for more resources
    }
  }
  # The tags are optional -->
  tags = {
    environment = "development"
    application = "myapp"
  }
}
