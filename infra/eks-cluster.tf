module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "21.6.1"

  name                                     = "myapp-eks-cluster"
  kubernetes_version                       = "1.30"
  endpoint_public_access                   = true
  enable_cluster_creator_admin_permissions = true

  vpc_id     = module.myapp-vpc.vpc_id
  subnet_ids = module.myapp-vpc.private_subnets

  enable_irsa = true # 🔥 REQUIRED

  addons = {
    vpc-cni    = { most_recent = true }
    kube-proxy = { most_recent = true }
    coredns    = { most_recent = true }
  }

  eks_managed_node_groups = {
    dev = {
      min_size       = 1
      max_size       = 3
      desired_size   = 2
      instance_types = ["t3.medium"]

      node_repair_config = {
        enabled = true
      }
    }
  }

  tags = {
    environment = "development"
    application = "myapp"
  }
}
