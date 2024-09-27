import boto3

# List all available AWS services
def list_all_services():
    session = boto3.session.Session()
    services = session.get_available_services()
    print("Available AWS Services:")
    for service in services:
        print(f"  - {service}")
    return services

# Scan through services and list their resources
def scan_service_resources():
    services = list_all_services()
    
    for service in services:
        try:
            print(f"\nScanning {service}...")
            client = boto3.client(service)
            
            # Try calling known describe or list methods (some of these vary)
            if service == 'ec2':
                response = client.describe_instances()
                for reservation in response['Reservations']:
                    for instance in reservation['Instances']:
                        print(f"  - EC2 Instance ID: {instance['InstanceId']}")
            elif service == 's3':
                response = client.list_buckets()
                for bucket in response['Buckets']:
                    print(f"  - S3 Bucket Name: {bucket['Name']}")
            elif service == 'lambda':
                response = client.list_functions()
                for function in response['Functions']:
                    print(f"  - Lambda Function Name: {function['FunctionName']}")
            elif service == 'rds':
                response = client.describe_db_instances()
                for db_instance in response['DBInstances']:
                    print(f" -  DBInstanceIdentifier: {db_instance['DBInstanceIdentifier']}")
 #           elif service == 'workspaces':
 #               response = client.describe_workspaces()
 #               for workspace in response['Workspaces']:
 #                   print(f" - Workspace ID: {workspace['WorkspaceId']}")
 #                   print(f"   - Directory ID: {workspace['DirectoryId']}")
 #                   print(f"   - User Name: {workspace['UserName']}")
 #                   print(f"   - State: {workspace['State']}")
 #                   print(f"   - Bundle ID: {workspace['BundleId']}")

            elif service == 'workspaces':
                response = client.describe_workspaces()
                for workspace in response['Workspaces']:
                    print(f" - Workspace ID: {workspace['WorkspaceId']}")
                    for key, value in workspace.items():
                        print(f"   -{key}: {value}")
                    
            # Add more services and their corresponding list/describe functions here            
            # For services without list or describe methods, we can skip or handle differently
            else:
                print(f"  - No known 'list' or 'describe' method for {service}")
        
        except Exception as e:
            print(f"  - Failed to retrieve resources for {service}: {e}")

# Run the service scanner
if __name__ == '__main__':
    scan_service_resources()
