import boto.ec2
import boto.route53
from collections import defaultdict
import time

# AWS Connection Stuff
AWS_REGION = 'us-east-1'

# Fill these in only if you aren't using ~/.boto like you should be...
#AWS_ACCESS_KEY = "NOPE"
#AWS_SECRET_ACCESS_KEY = "NOPE"

# ec2 Machine Defaults
DEFAULT_SIZE = "t2.medium"
#DEFAULT_SIZE = "t2.micro"
KEYNAME = 'pwnage' # Name of the keypair for this project
SECURITY_GROUP = 'sg-1d69e679' # ID for the security group 'not-a-good-idea'

# AMI IDs
WINDOWS_SERVER_2012_R2_BASE = "ami-b27830da"
WINDOWS_SERVER_2008_R2_BASE = "ami-188ac270"
WINDOWS_SERVER_2003_R2_SP2_SQL2005_IIS = "ami-c07931a8"
WINDOWS_7_WORKSTATION = ""
FREEBSD_10 = "ami-28cd5940"
UBUNTU_SERVER_1404_LTS = "ami-9a562df2"
UBUNTU_SERVER_1204_LTS = "ami-02df496b"
CENTOS_54 = "ami-96a818fe"
FEDORA = "ami-16ec977e"

# Random Settings
DRY_RUN = False
SUBNETS = ['subnet-ba009bcd', 'subnet-a5009bd2']
ROOT_DOMAIN = 'uwctf.ninja.'

# Define the machines you want spun up in each subnet here
def generate_machines(subnets):
    machines = list()
    for team_number, subnet_id in zip(range(1,len(subnets)+1), subnets) :
        machines.append(
            ec2Machine(
                WINDOWS_SERVER_2012_R2_BASE,
                subnet_id,
                tags = {
                    'Name': 'Breathtaking-Team{}'.format(team_number),
                    'project': 'pwnage',
                    'team': 'team{}'.format(team_number),
                    'DNS': 'breathtaking',
                    'ostype': 'win'
                    }
                )
           )
        machines.append(
            ec2Machine(
                WINDOWS_SERVER_2008_R2_BASE,
                subnet_id,
                tags = {
                    'Name': 'Excellent-Team{}'.format(team_number),
                    'project': 'pwnage',
                    'team': 'team{}'.format(team_number),
                    'DNS': 'excellent',
                    'ostype': 'win'
                    }
                )
           )
        machines.append(
            ec2Machine(
                WINDOWS_SERVER_2003_R2_SP2_SQL2005_IIS,
                subnet_id,
                tags = {
                    'Name': 'Marvelous-Team{}'.format(team_number),
                    'project': 'pwnage',
                    'team': 'team{}'.format(team_number),
                    'DNS': 'marvelous',
                    'ostype': 'win'
                    }
                )
           )
        machines.append(
            ec2Machine(
                FREEBSD_10,
                subnet_id,
                tags = {
                    'Name': 'Magnificent-Team{}'.format(team_number),
                    'project': 'pwnage',
                    'team': 'team{}'.format(team_number),
                    'DNS': 'magnificent',
                    'ostype': 'bsd'
                    }
                )
           )
        machines.append(
            ec2Machine(
                UBUNTU_SERVER_1404_LTS,
                subnet_id,
                tags = {
                    'Name': 'Wondrous-Team{}'.format(team_number),
                    'project': 'pwnage',
                    'team': 'team{}'.format(team_number),
                    'DNS': 'wondrous',
                    'ostype': 'linux'
                    }
                )
           )
        machines.append(
            ec2Machine(
                UBUNTU_SERVER_1204_LTS,
                subnet_id,
                tags = {
                    'Name': 'Splendid-Team{}'.format(team_number),
                    'project': 'pwnage',
                    'team': 'team{}'.format(team_number),
                    'DNS': 'splendidbsd',
                    'ostype': 'linux'
                    }
                )
           )
        machines.append(
            ec2Machine(
                CENTOS_54,
                subnet_id,
                tags = {
                    'Name': 'Grand-Team{}'.format(team_number),
                    'project': 'pwnage',
                    'team': 'team{}'.format(team_number),
                    'DNS': 'grand',
                    'ostype': 'linux'

                    }
                )
           )
        machines.append(
            ec2Machine(
                FEDORA,
                subnet_id,
                tags = {
                    'Name': 'Brilliant-Team{}'.format(team_number),
                    'project': 'pwnage',
                    'team': 'team{}'.format(team_number),
                    'DNS': 'brilliant',
                    'ostype': 'linux'
                    }
                )
           )
        ##machines.append(
            ##ec2Machine(
                ##UBUNTU_SERVER_1204_LTS,
                ##subnet_id,
                ##tags = {
                    ##'Name': 'Fabulous-Team{}'.format(team_number),
                    ##'project': 'pwnage',
                    ##'team': 'team{}'.format(team_number),
                    ##'DNS': 'fabulous'
                    ##}
                ##)
           ##)
        machines.append(
            ec2Machine(
                UBUNTU_SERVER_1404_LTS,
                subnet_id,
                tags = {
                    'Name': 'Outstanding-Team{}'.format(team_number),
                    'project': 'pwnage',
                    'team': 'team{}'.format(team_number),
                    'DNS': 'Outstanding',
                    'ostype': 'linux'
                    }
                )
           )
    return machines

def main():
    ec2conn = boto.ec2.connect_to_region(AWS_REGION)
    route53conn = boto.route53.connect_to_region(AWS_REGION)
    tags = spinup(ec2conn, generate_machines(SUBNETS))
    tag_instances(tags)
    add_dns(route53conn, tags)

def spinup(conn, machines):
    tags = defaultdict(dict)
    for machine in machines:
        reservation = conn.run_instances(
                machine.ami,
                min_count = machine.quantity,
                max_count = machine.quantity,
                key_name = machine.key_name,
                security_group_ids = machine.security_groups,
                instance_type = machine.instance_type,
                subnet_id = machine.subnet_id,
                private_ip_address = machine.private_ip_address,
                dry_run = DRY_RUN
                )
        print "Just asked for {}".format(machine)
        for instance in reservation.instances:
            tags[instance] = machine.tags

    while 'pending' in [i.update() for i in tags]:
        time.sleep(2)
    return tags

def tag_instances(tags):
    for instance in tags:
        for tag in tags[instance]:
            instance.add_tag(tag, tags[instance][tag])
        print "Just assigned {} ({}) the following tags: {}".format(
                instance.ip_address, instance.private_ip_address, tags[instance])

def add_dns(conn, tags):
    zone = conn.get_zone(ROOT_DOMAIN)
    for instance in tags:
        ip_address = instance.ip_address
        name = tags[instance]['DNS']
        team = tags[instance]['team']
        zone.add_record("A", "{}.{}.uwctf.ninja.".format(name, team), ip_address, ttl='45')

class ec2Machine(object):
    def __init__(self, ami, subnet_id, security_groups=[SECURITY_GROUP],
            quantity=1, key_name=KEYNAME, instance_type=DEFAULT_SIZE,
            private_ip="", tags={'Name': 'Unnamed', 'project': 'pwnage'}):
        self.ami = ami
        self.quantity = quantity
        self.key_name = key_name
        self.security_groups = security_groups
        self.instance_type = instance_type
        self.subnet_id = subnet_id
        self.private_ip_address = private_ip
        self.tags = tags

    def __repr__(self):
        return "ec2Machine({ami}, {subnet_id}, security_groups={security_groups}, quantity={quantity}, key_name={key_name}, tags={tags}".format(ami=self.ami,
                quantity=self.quantity, key_name=self.key_name,
                security_groups=self.security_groups,
                instance_type=self.instance_type, subnet_id=self.subnet_id,
                private_ip=self.private_ip_address, tags=self.tags)

if __name__ == "__main__":
    main()
