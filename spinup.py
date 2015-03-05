import boto.ec2
from collections import defaultdict
import time

# AWS Connection Stuff
AWS_REGION = 'us-east-1'

# Fill these in only if you aren't using ~/.boto like you should be...
#AWS_ACCESS_KEY = "NOPE"
#AWS_SECRET_ACCESS_KEY = "NOPE"

# ec2 Machine Defaults
DEFAULT_SIZE = "t2.medium"
KEYNAME = 'pwnage'
#SECURITY_GROUP = 'not-a-good-idea'
SECURITY_GROUP = 'sg-1d69e679'

# AMIs
WINDOWS_SERVER_2012_R2 = "ami-b27830da"
WINDOWS_SERVER_2008 = ""
WINDOWS_7_WORKSTATION = ""
UBUNTU_SERVER_1404_LTS = ""

# Random Settings
DRY_RUN = False
SUBNETS = ['subnet-ba009bcd'] # , 'subnet-a5009bd2']


def main():
    #conn = boto.ec2.connect_to_region(AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    conn = boto.ec2.connect_to_region(AWS_REGION)
    tags = defaultdict(dict)
    for machine in generate_machines(SUBNETS):
        reservation = conn.run_instances(
                machine.ami,
                min_count = machine.quantity,
                max_count = machine.quantity,
                key_name = machine.key_name,
                #security_groups = machine.security_groups,
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

    for instance in tags:
        for tag in tags[instance]:
            instance.add_tag(tag, tags[instance][tag])

    reservations = [res_id for res_id in tags]

def generate_machines(subnets):
    machines = list()
    for team_number, subnet_id in zip(range(len(subnets)), subnets) :
        machines.append(
            ec2Machine(
                WINDOWS_SERVER_2012_R2,
                subnet_id,
                tags = {
                    'Name': 'Breathtaking-Team{}'.format(team_number),
                    'project': 'pwnage',
                    'team': 'team{}'.format(team_number),
                    'DNS': 'breathtaking'
                    }
                )
            )
    print machines
    return machines

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
        return "ec2Machine({ami}, {subnet_id}, security_groups={security_groups}, quantity={quantity}, key_name={key_name}".format(ami=self.ami,
                quantity=self.quantity, key_name=self.key_name,
                security_groups=self.security_groups,
                instance_type=self.instance_type, subnet_id=self.subnet_id,
                private_ip=self.private_ip_address)

if __name__ == "__main__":
    main()
