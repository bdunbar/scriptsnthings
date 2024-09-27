import boto3

# List all available AWS services
def list_all_services():
    session = boto3.session.Session()
    services = session.get_available_services()
    print("Available AWS Services:")
    for service in services:
        print(f"  - {service}")

# List of all regions
def get_all_regions():
    ec2 = boto3.client('ec2')
    response = ec2.describe_regions()
    regions = [region['RegionName'] for region in response['Regions']]
    return regions

# EC2 instances across all regions
def list_ec2_instances():
    regions = get_all_regions()
    for region in regions:
        ec2 = boto3.client('ec2', region_name=region)
        instances = ec2.describe_instances()
        print(f"EC2 Instances in region: {region}")
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                print(f"  - Instance ID: {instance['InstanceId']} State: {instance['State']['Name']}")

# S3 buckets (S3 is global, not regional)
def list_s3_buckets():
    s3 = boto3.client('s3')
    buckets = s3.list_buckets()
    print("S3 Buckets (Global):")
    for bucket in buckets['Buckets']:
        print(f"  - {bucket['Name']}")

# RDS instances across all regions
def list_rds_instances():
    regions = get_all_regions()
    for region in regions:
        rds = boto3.client('rds', region_name=region)
        instances = rds.describe_db_instances()
        print(f"RDS Instances in region: {region}")
        for db_instance in instances['DBInstances']:
            print(f"  - DBInstanceIdentifier: {db_instance['DBInstanceIdentifier']}")

# Lambda functions across all regions
def list_lambda_functions():
    regions = get_all_regions()
    for region in regions:
        lambda_client = boto3.client('lambda', region_name=region)
        functions = lambda_client.list_functions()
        print(f"Lambda Functions in region: {region}")
        for function in functions['Functions']:
            print(f"  - {function['FunctionName']}")

# CloudFormation stacks across all regions
def list_cloudformation_stacks():
    regions = get_all_regions()
    for region in regions:
        cloudformation = boto3.client('cloudformation', region_name=region)
        stacks = cloudformation.describe_stacks()
        print(f"CloudFormation Stacks in region: {region}")
        for stack in stacks['Stacks']:
            print(f"  - {stack['StackName']}")

# Workspaces across all regions
def list_workspaces():
    regions = get_all_regions()
    for region in regions:
        workspace_client = boto3.client('workspaces', region_name=region)
        workspace = workspace_client.list_somethings()

# Run all the inventory functions
if __name__ == '__main__':
    list_all_services()
    list_ec2_instances()
    list_s3_buckets()
    list_rds_instances()
    list_lambda_functions()
    list_cloudformation_stacks()
