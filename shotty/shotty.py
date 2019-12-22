import boto3
import click
import botocore

session = boto3.Session(profile_name='frrivero-belion')
ec2 = session.resource('ec2')


@click.group()
def cli():
    """Shotty CLI commands"""


@cli.group('volumes')
def volumes():
    """Commands for volumes"""


@cli.group('instances')
def instances():
    """Commands for instances"""


@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""


@instances.command('list')
@click.option('--project', default=None,
              help='Only instances for project (tag Project:<name>)')
def list_instances(project):
    """List EC2 instances"""

    instances = get_instances(project)

    for i in instances:
        tags = {t['Key']: t['Value'] for t in i.tags or []}
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.root_device_type,
            i.public_dns_name or 'no_dns',
            tags.get('Project', '<no project>')
        )))
    return


def get_instances(project):
    if project:
        filters = [{'Name': 'tag:Project', 'Values': [project]}]
        return ec2.instances.filter(Filters=filters)

    return ec2.instances.all()


@instances.command('stop')
@click.option('--project', default=None, help='Only instances for project')
def stop_instances(project):
    """Stop EC2 instances"""
    instances = get_instances(project)
    for i in instances:
        print("Stopping {0}  ...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print(e)
    return


@instances.command('start')
@click.option('--project', default=None, help='Only instances for project')
def stop_instances(project):
    """Start EC2 instances"""
    instances = get_instances(project)
    for i in instances:
        print("Starting {0}  ...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print(e)
    return


def get_volumes(project):
    if project:
        filters = [{'Name': 'tag:Project', 'Values': [project]}]
        return ec2.volumes.filter(Filters=filters)

    return ec2.volumes.all()


@volumes.command('list')
@click.option('--project', default=None, help='Only volumes for project')
def list_volumes(project):
    """List Volumes"""
    for i in get_volumes(project):
        print(', '.join((
            i.id,
            str(i.size) + "GB",
            i.state,
            ("Not_Encrypted", "Encrypted")[i.encrypted],  # (if_test_is_false, if_test_is_true)[test]
            i.encrypted and "Encrypted" or "Not_Encrypted",
        )))
    return


def get_snapshots(project):
    filters = project and [{'Name': 'tag:Project', 'Values': [project]}] or []
    result = []
    for v in get_volumes(project):
        for s in v.snapshots.filter(Filters=filters):
            result.append(s)
    return result


@snapshots.command('list')
@click.option('--project', default=None, help='Only snapshots for project')
@click.option('--all', 'list_all', default=False, idFlag=True, help='If true not just the most recent snapshot will be '
                                                                    'returned')
def list_snapshots(project, list_all):
    """List Snapshots"""
    for i in get_snapshots(project):
        # print(i)
        print(', '.join((
            i.id,
            str(i.volume_size) + "GB",
            i.state,
            i.progress,
            ("Not_Encrypted", "Encrypted")[i.encrypted],  # (if_test_is_false, if_test_is_true)[test]
            i.encrypted and "Encrypted" or "Not_Encrypted",
        )))
        if i.state == 'completed' and not list_all: break
    return


@snapshots.command('create')
@click.option('--project', default=None, help='Only snapshots for project')
def create_snapshots(project):
    """List Volume Snapshots"""
    filters = project and [{'Name': 'tag:Project', 'Values': [project]}] or []
    for i in get_instances(project):
        i.stop()
        print("Stopping instance: {0}".format(i.id))
        i.wait_until_stopped()
        for v in i.volumes.filter(Filters=filters):
            if has_pending_snapshot(v):
                print("     Skipping vol {0} because has pending snapshots".format(v.id))
                continue
            print("     Creating snapshot for volume {0} of instance: {1}".format(v.id, i.id))
            v.create_snapshot(Description='Created with Shotty')

        i.start()
        print("Starting instance: {0}".format(i.id))
        i.wait_until_running()
        print("Instance {0} started".format(i.id))
    print("Job is done!!!")
    return


def has_pending_snapshot(vol):
    snapshots = vol.snapshots.all()
    return snapshots and snapshots[0].state == 'pending'


if __name__ == '__main__':
    cli()
