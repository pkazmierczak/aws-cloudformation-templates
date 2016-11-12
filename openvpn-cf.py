from troposphere import (Base64, Join, FindInMap,
                         Parameter, Ref, Tags, Template)

import troposphere.ec2 as ec2

# Mappings of OpenVPN AMIs
OPENVPN_AMI = {
    'ap-northeast-1': {"AMI": 'ami-5ea72b5e'},   # Asia Pacific (Tokyo)
    'ap-southeast-1': {"AMI": 'ami-365c5764'},   # Asia Pacific (Singapore)
    'ap-southeast-2': {"AMI": 'ami-831d51b9'},   # Asia Pacific (Sydney)
    'eu-central-1':   {"AMI": 'ami-507f7e4d'},   # EU (Frankfurt)
    'eu-west-1':      {"AMI": 'ami-03644074'},   # EU (Ireland)
    'sa-east-1':      {"AMI": 'ami-4fd55f52'},   # South America (Sao Paulo)
    'us-east-1':      {"AMI": 'ami-5fe36434'},   # US East (N. Virginia)
    'us-west-1':      {"AMI": 'ami-8bf40fcf'},   # US West (N. California)
    'us-west-2':      {"AMI": 'ami-9fe2f2af'}    # US West (Oregon)
}

ASCII_CHAR = "[\\x20-\\x7E]*"
INVALID_ASCII_MSG = "can contain only ASCII characters."

t = Template()

t.add_version("2010-09-09")

t.add_description("OpenVPN server template")

Project = t.add_parameter(Parameter(
    "Project",
    Type="String",
    Description="OpenVPN-server",
    Default="OpenVPN-server",
    MinLength="1",
    MaxLength="255",
    AllowedPattern=ASCII_CHAR,
    ConstraintDescription=INVALID_ASCII_MSG,
))

KeyName = t.add_parameter(Parameter(
    "KeyName",
    ConstraintDescription="must be the name of an existing EC2 KeyPair.",
    Type="AWS::EC2::KeyPair::KeyName",
    Default="openvpn",
    Description="Name of an existing EC2 KeyPair to enable SSH access to the instances",
))

InstanceType = t.add_parameter(Parameter(
    "InstanceType",
    Default="t2.micro",
    ConstraintDescription="must be a valid EC2 instance type.",
    Type="String",
    Description="Instance type for EC2 instance.",
    AllowedValues=["t2.micro", "t2.medium", "m3.medium", "m3.large", "m3.xlarge", "m3.2xlarge"],
))

t.add_mapping("AWSRegion2AMI", OPENVPN_AMI)

VPNSecurityGroup = t.add_resource(ec2.SecurityGroup(
    "VPNSecurityGroup",
    SecurityGroupIngress=[
        # By default 22 is locked for security reasons
        # {"ToPort": "22", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "22"},
        {"ToPort": "443", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "443"},
        {"ToPort": "1194", "IpProtocol": "udp", "CidrIp": "0.0.0.0/0", "FromPort": "1194"}],
    GroupDescription="Enable SSH access to the instance and VPN access via configured port. ",
    Tags=Tags(
        Name=Join("-", ["SG-VPN", Ref(Project)]),
    ),
))

OpenVPNInstance = t.add_resource(ec2.Instance(
    "OpenVPNInstance",
    ImageId=FindInMap("AWSRegion2AMI", Ref("AWS::Region"), "AMI"),
    SecurityGroups=[Ref(VPNSecurityGroup)],
    KeyName=Ref(KeyName),
    InstanceType=Ref(InstanceType),
    UserData=Base64(Join("", [
        "public_hostname=openvpn\n",
        "admin_user=openvpn\n",
        "admin_pw=openvpn\n",
        "reroute_gw=1\n",
        "reroute_dns=1\n"
        ])),
    Tags=Tags(
        Name=Join("-", ["EC2-VPN", Ref(Project)]),
    ),
))

print(t.to_json())
