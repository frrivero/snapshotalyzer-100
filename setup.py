from setuptools import setup

setup(
    name='snapshotylezer-100',
    version='0.1',
    author='Robin hood',
    author_email='me@the.com',
    description='Some EC2 snapshot tools',
    license='GPLv3+',
    packages=['shotty'],
    url='https://github.com/frrivero/snapshotalyzer-100',
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        shotty=shotty.shotty:cli
    '''
)
