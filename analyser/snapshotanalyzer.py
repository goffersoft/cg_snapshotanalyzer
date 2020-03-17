import boto3
import click 

def get_aws_session(profile_name):
    return boto3.Session(profile_name=profile_name)

def get_aws_resource(session, resource_name):
    return session.resource(resource_name)

def get_ec2_instances(ec2_resource_object, project):
    instances = []

    if (project == None):
        instlist = ec2_resource_object.instances.all()
    else:
        filters=[{'Name':'tag:Project', 'Values':[project]}]
        instlist = ec2_resource_object.instances.filter(Filters=filters)

    for i in instlist:
        instances.append(i)
    return instances 

def print_ec2_instances(ec2_instances):
    for i in ec2_instances:
        tags = {t['Key']:t['Value'] for t in i.tags or []}
        print(','.join((
                 i.id,
                 i.instance_type,
                 i.placement['AvailabilityZone'],
                 i.state['Name'],
                 i.public_dns_name,
                 'Project' + ':' + tags.get('Project', '<no project>') ))
             )
    return

@click.group()
def instances():
    """Commands for Instances"""

@instances.command('start')
@click.option('--project', default=None,
               help='only isntances for project(tag Project:<name>')
def start_instances(project):
    """ Start EC2 Instances """

    ec2_resource_object = init('goffer-snapshotanalyzer', 'ec2')
    ec2_instances = get_ec2_instances(ec2_resource_object, project)
    for i in ec2_instances:
        print('Starting... {0}'.format(i.id))
        i.start()

@instances.command('stop')
@click.option('--project', default=None,
              help='only instances for project(tag Project:<name>)')
def stop_instances(project):
    """ Stop EC2 Instances """
    ec2_resource_object = init('goffer-snapshotanalyzer', 'ec2')
    ec2_instances = get_ec2_instances(ec2_resource_object, project)
    
    for i in ec2_instances:
        print("Stopping... {0}".format(i.id))
        i.stop()

@instances.command('list')
@click.option('--project', default=None,
        help='Only instances for project (tag Project:<name>)')
def list_ec2_instances(project):
    """List EC2 Instances"""
    ec2_resource_object = init('goffer-snapshotanalyzer', 'ec2')
    ec2_instances = get_ec2_instances(ec2_resource_object, project)
    print_ec2_instances(ec2_instances)

def init(profile_name, resource_name):
    session = get_aws_session(profile_name)
    return get_aws_resource(session, resource_name)

if __name__ == "__main__":
    instances()
