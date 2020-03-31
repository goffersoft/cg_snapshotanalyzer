import boto3
import click
import botocore

g_aws_session = None
g_ec2_resource = None

def get_session(pname):
    """ Get boto3 session associated with aws profile name """

    return boto3.Session(profile_name=pname)

def get_resource(session, rname):
    """ Get boto3 resource associated with resource name """

    return session.resource(rname)

def get_instances(resource, project):
    """ Get instances associated with resource.
        Conditionally filter by project name """

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

def list_ec2_snapshots(project, list_all):
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
                if(s.state == 'completed' and not list_all):
                    break
          

    return

def is_instance_running(instance):
    """ Determine if the instnace is running or not """

    if instance.state['Name'] == 'running': return True

    return False
    

def has_pending_snapshots(volume):
    """ Utility function to check if there
        are any pending snapshots for this instance """

    snapshots = list(volume.snapshots.all()) 
    return snapshots and snapshots[0] == 'pending'

def create_ec2_snapshots(project):
    """ create snapshots associated with EC2 instances """

    for i in get_instances(g_ec2_resource, project):
        stopped = False
        if is_instance_running(i):
            if stop_ec2_instance(i, True):
                stopped = True
            else:
                continue
        for v in i.volumes.all():
            if has_pending_snapshots(v):
                print('skipping {0}, snapshot\
                         already in progress'.format(v.id))
                continue
            try:
                print('creating snapshot...({0}, {1})'.format(i,v))
                v.create_snapshot(Description='created by \
                              snapshotanalyzer app')
            except botocore.exceptions.ClientError as e:
                print('Could Not Create Snapshot for {0}-{1} : {2}'\
                          .format(i,v,e))
        if stopped:
            start_ec2_instance(i, True)

    return

def stop_ec2_instance(instance, wait):
    """ Stop ec2 instance """

    try:
        print('Stopping {0}...'.format(instance.id))
        instance.stop()
        if wait: instance.wait_until_stopped()
        return True
    except e:
        print('couldnot stop {0} : '.format(instance.id) + str(e))
        return False 

def start_ec2_instance(instance, wait):
    """ Start ec2 instance """

    try:
        print('Starting {0}...'.format(instance.id))
        instance.start()
        if wait: instance.wait_until_running()
        return True
    except e:
        print('couldnot start {0} : '.format(instance.id) + str(e))
        return False

def start_ec2_instances(project):
    """ Start EC2 instances """

    for i in get_instances(g_ec2_resource, project):
        start_ec2_instance(i, False) 
    
    return 

def stop_ec2_instances(project):
    """ Stop EC2 instances """

    for i in get_instances(g_ec2_resource, project):
        stop_ec2_instance(i, False)

    return

def reboot_ec2_instances(project):
    """ Reboot EC2 Instances """

    for i in get_instances(g_ec2_resource, project): 
        if not stop_ec2_instance(i, True): continue
        start_ec2_instance(i, False)

    return

def init(pname, rname):
    """ Initialze boto3 """

    session = get_session(pname)
    resource = get_resource(session, rname)

    return (session, resource)

@click.group()
@click.option('--profile', default=None,
        help='profile name to use while initializing the boto3 package')
def cli(profile):
    " Snapshot Command Line Interface """
    
    global g_aws_session
    global g_ec2_resource

    if profile == None: pname='goffer-snapshotanalyzer'
    else: pname = profile

    (g_aws_session, g_ec2_resource) = \
             init(pname, 'ec2')

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
@click.option('--all', 'list_all', default=False, is_flag=True,
              help='list all snapshots')
def list_snapshots(project, list_all):
    """ List snapshots associated with all instances (EC2 Only) """
    
    list_ec2_snapshots(project, list_all)

    return

@snapshots.command('create')
@click.option('--project', default=None,
              help='create snapshots for all volumes associated with \
                    instances (ec2 only) for project tag:Project:<name>')
@click.option('--force', is_flag=True,
        help='create snapshots associated with all ec2 instances')
def create_snapshots(project, force):
    """ Create snapshots associated with all instances (EC2 Only) """

    if not force and project == None:
        print('Please Specify Project Name associated with Instances')
        return

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

@instances.command('reboot')
@click.option('--project', default=None,
       help='start all instances(ec2 only) for project tag:Project:<name>')
@click.option('--force', is_flag=True,
        help='reboot all ec2 instances for all projects')
def reboot_instances(project, force):
    """ Reboot instances (EC2 only) """

    if not force and project == None:
        print('Please Specify Project Name associated with Instances')
        return

    reboot_ec2_instances(project)

    return

@instances.command('start')
@click.option('--project', default=None,
       help='start all instances(ec2 only) for project tag:Project:<name>')
@click.option('--force', is_flag=True,
        help='start all ec2 instances for all projects')
def start_instances(project, force):
    """ Start instances (EC2 only) """

    if not force and project == None:
        print('Please Specify Project Name associated with Instances')
        return
    
    start_ec2_instances(project)

    return

@instances.command('stop')
@click.option('--project', default=None,
        help='stop all instances(ec2 only) for project tag:Project:<name>')
@click.option('--force', is_flag=True,
        help='stop all ec2 instances for all projects')
def stop_instances(project, force):
    """ Stop instances (EC2 only) """

    if not force and project == None:
        print('Please Specify Project Name associated with Instances')
        return

    stop_ec2_instances(project)

    return

if __name__ == "__main__":
    cli()
