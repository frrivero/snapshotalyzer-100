import boto3
import click

session = boto3.Session(profile_name='frrivero-belion')
ec2 = session.resource('ec2')


@click.group()
def instances():
    """Commands for instances"""


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
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
    return instances


@instances.command('stop')
@click.option('--project', default=None, help='Only instances for project')
def stop_instances(project):
    """Stop EC2 instances"""
    instances = get_instances(project)
    for i in instances:
        print("Stopping {0}  ...".format(i.id))
        i.stop()
    return


@instances.command('start')
@click.option('--project', default=None, help='Only instances for project')
def stop_instances(project):
    """Start EC2 instances"""
    instances = get_instances(project)
    for i in instances:
        print("Starting {0}  ...".format(i.id))
        i.start()
    return


if __name__ == '__main__':
    instances()
