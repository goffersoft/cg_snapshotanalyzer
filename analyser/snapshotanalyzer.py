import boto3

def get_aws_session(profile_name):
    return boto3.Session(profile_name=profile_name)

def get_aws_resource(session, resource_name):
    return session.resource(resource_name)

def get_ec2_instances(ec2_resource_object):
    instances = []
    for i in ec2_resource_object.instances.all():
        instances.append(i)
    return instances 

def main_loop():
    session = get_aws_session('goffer-snapshotanalyzer')
    ec2_resource  = get_aws_resource(session, 'ec2')
    ec2_instances = get_ec2_instances(ec2_resource)
    for i in ec2_instances: print(i)

if __name__ == "__main__":
    main_loop()
