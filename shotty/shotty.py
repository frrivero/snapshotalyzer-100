import boto3
import pprint

if __name__ == '__main__':
    session = boto3.Session(profile_name='frrivero-belion')
    ec2 = session.resource('ec2')

    pp = pprint.PrettyPrinter(indent=4)
    for i in ec2.instances.all():
        pp.pprint(i)
