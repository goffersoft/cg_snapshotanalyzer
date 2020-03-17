import boto3
import click 

def get_aws_session(profile_name):
    return boto3.Session(profile_name=profile_name)

def get_aws_resource(session, resource_name):
    return session.resource(resource_name)

def get_ec2_instances(ec2_resource_object):
    instances = []
    for i in ec2_resource_object.instances.all():
        instances.append(i)
    return instances 

def print_ec2_instances(ec2_instances):
    for i in ec2_instances:
        print(','.join((
                 i.id,
                 i.instance_type,
                 i.placement['AvailabilityZone'],
                 i.state['Name'],
                 i.public_dns_name))
             )

    return

@click.command()
def list_ec2_instances():
    """List EC2 Instances"""
    ec2_resource_object = init('goffer-snapshotanalyzer', 'ec2')
    ec2_instances = get_ec2_instances(ec2_resource_object)
    print_ec2_instances(ec2_instances)

def init(profile_name, resource_name):
    session = get_aws_session(profile_name)
    return get_aws_resource(session, resource_name)

if __name__ == "__main__":
    list_ec2_instances()
