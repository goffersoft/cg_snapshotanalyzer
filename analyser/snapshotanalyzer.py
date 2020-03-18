import boto3
import click

g_aws_session = None
g_ec2_resource = None

def get_session(pname):
    return boto3.Session(profile_name=pname)

def get_resource(session, rname):
    return session.resource(rname)

def get_instances(resource, project):
    if (project == None):
        return list(resource.instances.all())
    
    filter=[{'Name':'tag:Project', 'Values':[project]}]

    return list(resource.instances.filter(Filters=filter))

def list_ec2_instances(project):
    """ List EC2 instances """
    for i in get_instances(g_ec2_resource, project):
        tags = {t['Key']:t['Value'] for t in i.tags or []}
        print(','.join((i.id,
                        i.instance_type,
                        i.public_dns_name,
                        i.placement['AvailabilityZone'],
                        i.state['Name'],
                        tags.get('Project', '<no-project>'))))
    return

def start_ec2_instances(project):
    """ Start EC2 instances """
    for i in get_instances(g_ec2_resource, project):
        print('Starting...{0}'.format(i.id))
        i.start() 
    
    return 

def stop_ec2_instances(project):
    """ Stop EC2 instances """
    for i in get_instances(g_ec2_resource, project):
        print('Stopping...{0}'.format(i.id))
        i.stop() 
    
    return 

def init(pname, rname):
    """ initialze boto3 """

    session = get_session(pname)
    resource = get_resource(session, rname)

    return (session, resource)

@click.group()
def instances():
    """ Commands related to instances """

    return

@instances.command('list')
@click.option('--project', default=None,
           help='print all ec2 isntances for project tag:Project:<name>')
def list_instances(project):
    """ List instances """

    list_ec2_instances(project)

    return

@instances.command('start')
@click.option('--project', default=None,
             help='start all ec2 isntances for project tag:Project:<name>')
def start_instances(project):
    """ Start instances """
    
    start_ec2_instances(project)

    return

@instances.command('stop')
@click.option('--project', default=None,
             help='stop all ec2 isntances for project tag:Project:<name>')
def stop_instances(project):
    """ Stop instances """

    stop_ec2_instances(project)

    return

if __name__ == "__main__":
    (g_aws_session, g_ec2_resource) = \
             init('goffer-snapshotanalyzer', 'ec2')
    instances()
