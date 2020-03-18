import boto3
import click
import botocore

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
                        'Project='+tags.get('Project', '<no-project>'))))
    return

def list_ec2_volumes(project):
    """ List volumes associated with EC2 instances """

    for i in get_instances(g_ec2_resource, project):
        tags = {t['Key']:t['Value'] for t in i.tags or []}
        for v in i.volumes.all():
            print(','.join((
                        v.id,
                        i.id,
                        v.state,
                        str(v.size) + 'GiB',
                        v.encrypted and 'Encrypted' or 'Not Encrypted',
                        'Project='+tags.get('Project', '<no-project>'))))
    
    return

def list_ec2_snapshots(project):
    """ List snapshots associated with EC2 instances """
    
    for i in get_instances(g_ec2_resource, project):
        tags = {t['Key']:t['Value'] for t in i.tags or []}
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(','.join((
                        s.id,
                        v.id,
                        i.id,
                        s.state,
                        s.progress,
                        s.start_time.strftime('%c'),
                        'Project='+tags.get('Project', '<no-project>'))))

    return

def create_ec2_snapshots(project):
    """ create snapshots associated with EC2 instances """

    for i in get_instances(g_ec2_resource, project):
        print('Stopping {0}...'.format(i))
        i.stop()
        i.wait_until_stopped()
        for v in i.volumes.all():
            print('creating snapshot...({0}, {1})'.format(i,v))
            v.create_snapshot(Description='created by \
                              snapshotanalyzer app')
        print('Starting {0}...'.format(i))
        i.start()
        i.wait_until_running() 
    return

def start_ec2_instances(project):
    """ Start EC2 instances """
    for i in get_instances(g_ec2_resource, project):
        print('Starting...{0}'.format(i.id))
        try:
            i.start() 
        except botocore.exceptions.ClientError as e:
            print('couldnot start {0} : '.format(i.id) + str(e))
            continue
    
    return 

def stop_ec2_instances(project):
    """ Stop EC2 instances """
    for i in get_instances(g_ec2_resource, project):
        print('Stopping...{0}'.format(i.id))
        try:
            i.stop() 
        except botocore.exceptions.ClientError as e:
            print('couldnot stop {0} : '.format(i.id) + str(e))
            continue
    
    return 

def init(pname, rname):
    """ initialze boto3 """

    session = get_session(pname)
    resource = get_resource(session, rname)

    return (session, resource)

@click.group()
def cli():
   " Snapshot Command Line Interface """
   
   return

@cli.group()
def instances():
    """ Commands related to instances """

    return

@cli.group()
def volumes():
    """ Commands related to volumes"""

    return

@cli.group()
def snapshots():
    """ Commands related to snapshots"""

    return

@snapshots.command('list')
@click.option('--project', default=None,
              help='print all volumes associated with \
                    instances (ec2 only) for project tag:Project:<name>')
def list_snapshots(project):
    """ List snapshots associated with all instances (EC2 Only) """
    
    list_ec2_snapshots(project)

    return

@snapshots.command('create')
@click.option('--project', default=None,
              help='create snapshots for all volumes associated with \
                    instances (ec2 only) for project tag:Project:<name>')
def create_snapshots(project):
    """ create snapshots associated with all instances (EC2 Only) """

    create_ec2_snapshots(project)

@volumes.command('list')
@click.option('--project', default=None,
              help='print all volumes associated with \
                    instances (ec2 only) for project tag:Project:<name>')
def list_volumes(project):
    """ List volumes associated with all instances (EC2 Only) """
    
    list_ec2_volumes(project)

    return

@instances.command('list')
@click.option('--project', default=None,
     help='print all instances(ec2 only) for project tag:Project:<name>')
def list_instances(project):
    """ List instances (EC2 Only) """

    list_ec2_instances(project)

    return

@instances.command('start')
@click.option('--project', default=None,
       help='start all instances(ec2 only) for project tag:Project:<name>')
def start_instances(project):
    """ Start instances (EC2 only) """
    
    start_ec2_instances(project)

    return

@instances.command('stop')
@click.option('--project', default=None,
        help='stop all instances(ec2 only) for project tag:Project:<name>')
def stop_instances(project):
    """ Stop instances (EC2 only) """

    stop_ec2_instances(project)

    return

if __name__ == "__main__":
    (g_aws_session, g_ec2_resource) = \
             init('goffer-snapshotanalyzer', 'ec2')
    cli()
