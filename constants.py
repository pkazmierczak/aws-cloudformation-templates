#!/usr/bin/env python
#
# Generic set of useful constants and expressions for Cloudformation
#


VALID_IP_REGEX            = "\\d{1,3}+\\.\\d{1,3}+\\.\\d{1,3}+\\.\\d{1,3}"
INVALID_IP_MSG            = "Must be valid IP address xx.xx.xx.xx"

VALID_CIDR_IP_REGEX       = VALID_IP_REGEX + "/\\d\\d"
INVALID_CIDR_IP_MSG       = "Must be a valid CIDR IP address xx.xx.xx.xx/xx"

VALID_KEYNAME_REGEX       = "[\\.-_ a-zA-Z0-9]*"
INVALID_KEYNAME_MSG       = "Must be a valid key name; can contain only alphanumeric characters, spaces, dashes, dot  and underscores"


VALID_DNS_REGEX       = "(?:[a-z][a-z-]+\\.)?[a-z][a-z-]+\\.([a-z]{2,6})$"
INVALID_DNS_MSG       = "Must be a valid domain name"



# for internal construction
EIGHT_DIGIT_HEX           = "[a-f0-9]{8}"


VALID_DIGIT_REGEX         = "[0-9]*"
INVALID_DIGIT_MSG         = "can contain only Digit characters."

ASCII_CHAR                = "[\\x20-\\x7E]*"
INVALID_ASCII_MSG         = "can contain only ASCII characters."


# eg vpc-a1b2c3d4
VALID_VPC_REGEX           = "vpc-" + EIGHT_DIGIT_HEX
INVALID_VPC_MSG           = "Must be valid VPC identifier vpc-xxxxxxxx"

# eg vpc-a1b2c3d4
VALID_DB_REGEX           = "[a-zA-Z][a-zA-Z0-9]*"
INVALID_DB_MSG           = "must begin with a letter and contain only alphanumeric characters."

# eg rtb-a1b2c3d4
VALID_RTB_REGEX           = "rtb-" + EIGHT_DIGIT_HEX
INVALID_RTB_MSG           = "Must be valid route table identifier rtb-xxxxxxxx"

# eg subnet-a1b2c3d4
VALID_SUBNET_REGEX        = "subnet-" + EIGHT_DIGIT_HEX
INVALID_SUBNET_MSG        = "Must be valid subnet identifier subnet-xxxxxxxx"

# eg sg-a1b2c3d4
VALID_SG_REGEX            = "sg-" + EIGHT_DIGIT_HEX
INVALID_SG_MSG            = "Must be valid security group identifier sg-xxxxxxxx"

# eg rtb-a1b2c3d4
VALID_AMI_REGEX           = "ami-" + EIGHT_DIGIT_HEX
INVALID_AMI_MSG           = "Must be valid AMI identifier ami-xxxxxxxx"

# eg eipalloc-a1b2c3d4
VALID_EIPALLOC_REGEX      = "eipalloc-" + EIGHT_DIGIT_HEX
INVALID_EIPALLOC_MSG      = "Must be valid elastic IP allocation identifier eipalloc-xxxxxxxx"

# eg eni-a1b2c3d4
VALID_ENI_REGEX           = "eni-" + EIGHT_DIGIT_HEX
INVALID_ENI_MSG           = "Must be valid network interface identifier eni-xxxxxxxx"




#Needs to be updated with latest instance lisiting
INSTANCE_SIZES = [
    "t1.micro", "m1.small", "m1.medium", "m1.large",
    "m1.xlarge", "m2.xlarge", "m2.2xlarge", "m2.4xlarge",
    "m3.xlarge", "m3.2xlarge", "c1.medium", "c1.xlarge",
    "c3.large", "c3.xlarge", "c3.2xlarge", "c3.4xlarge",
    "c3.8xlarge", "cc2.8xlarge", "cr1.8xlarge", "hi1.4xlarge",
    "hs1.8xlarge", "i2.xlarge", "i2.2xlarge", "i2.4xlarge", "i2.8xlarge",
    "cg1.4xlarge", "g2.2xlarge",
]

INVALID_INSTANCE_TYPE_MSG = "Must be valid EC2 instance type"

AWS_NAT_AMI = {
    "eu-west-1": { "AMI": "ami-f3e30084" },
    "eu-central-1": { "AMI": "ami-1e073a03" },
    "us-east-1": { "AMI": "ami-ad227cc4" },
    "us-west-1": { "AMI": "ami-d69aad93" },
    "us-west-2": { "AMI": "ami-f032acc0" },
    "sa-east-1": { "AMI": "ami-d78325ca" },
    "ap-northeast-1": { "AMI": "ami-cd43d9cc" },
    "ap-southeast-1": { "AMI": "ami-f22772a0" },
    "ap-southeast-2": { "AMI": "ami-3bae3201" },
    # Ensure this list is up to date/correct
}

OPENVPN_AS_AMI = {
    "eu-west-1": { "AMI": "ami-89d83afe" },
    "us-east-1": { "AMI": "ami-ff6b3096" },
    "us-west-1": { "AMI": "ami-6c0b3d29" },
    "us-west-2": { "AMI": "ami-c8039bf8" },
    "sa-east-1": { "AMI": "ami-6d4ee870" },
    "ap-northeast-1": { "AMI": "ami-172d4916)" },
    "ap-southeast-1": { "AMI": "ami-3c9bce6e)" },
    "ap-southeast-2": { "AMI": "ami-db73efe1" },

}


CENTOS_7_AMI = {
 'ap-northeast-1': {"AMI": 'ami-89634988'},   # Asia Pacific (Tokyo)
 'ap-southeast-1': {"AMI": 'ami-aea582fc'},   # Asia Pacific (Singapore)
 'ap-southeast-2': {"AMI": 'ami-bd523087'},   # Asia Pacific (Sydney)
 'eu-central-1':   {"AMI": 'ami-7cc4f661'},   # EU (Frankfurt)
 'eu-west-1':      {"AMI": 'ami-e4ff5c93'},   # EU (Ireland)
 'sa-east-1':      {"AMI": 'ami-bf9520a2'},   # South America (Sao Paulo)
 'us-east-1':      {"AMI": 'ami-96a818fe'},   # US East (N. Virginia)
 'us-west-1':      {"AMI": 'ami-6bcfc42e'},   # US West (N. California)
 'us-west-2':      {"AMI": 'ami-c7d092f7'}   # US West (Oregon)
}


UBUNTU_14_AMI = {
 'ap-northeast-1': {"AMI": 'ami-936d9d93'},   # Asia Pacific (Tokyo)
 'ap-southeast-1': {"AMI": 'ami-96f1c1c4'},   # Asia Pacific (Singapore)
 'ap-southeast-2': {"AMI": 'ami-69631053'},   # Asia Pacific (Sydney)
 'eu-central-1':   {"AMI": 'ami-accff2b1'},   # EU (Frankfurt)
 'eu-west-1':      {"AMI": 'ami-47a23a30'},   # EU (Ireland)
 'sa-east-1':      {"AMI": 'ami-4d883350'},   # South America (Sao Paulo)
 'us-east-1':      {"AMI": 'ami-d05e75b8'},   # US East (N. Virginia)
 'us-west-1':      {"AMI": 'ami-df6a8b9b'},   # US West (N. California)
 'us-west-2':      {"AMI": 'ami-5189a661'}   # US West (Oregon)
}

import re

def print_json(json):
    json = re.sub(r'{\n\s+(\"Ref.*)\n\s+', r"{\1",json,flags=re.MULTILINE)
    json = re.sub(r'\n\s+\[\n\s+(.*)\n\s+(.*)\n\s+]', r'[ \1 \2 ]',json,flags=re.MULTILINE)
    json = re.sub(r'Fn::GetAtt": \[\n\s+(.*)\n\s+(.*)\n\s+\]', r'Fn::GetAtt": [ \1 \2 ]',json,flags=re.MULTILINE)
    json = re.sub(r'Fn::Join": \[\n\s+(.*)\n\s+\]', r'Fn::Join": [ \1 ]',json,flags=re.MULTILINE)
    json = re.sub(r'Fn::Join": \[\n\s+(.*)\n\s+\[\n\s+(.*)\n\s+\{\n\s+(.*)\n\s+}\n\s+\]\n\s+\]', r'Fn::Join": [ \1 \2 \3 ]',json,flags=re.MULTILINE)
    json = re.sub(r'"Tags": \[\n\s+{(\n\s+)("Key".*)(\n\s+)("Value".*)(\n\s+)}\n\s+]', r'"Tags": [{ \1\2\3\4\5 }]',json,flags=re.MULTILINE)
    json = re.sub(r'"Tags": \[\n\s+{(\n\s+)("Key".*)(\n\s+)("PropagateAtLaunch".*)(\n\s+)("Value".*)(\n\s+)}\n\s+]', r'"Tags": [{ \1\2\3\4\5\6\7 }]',json,flags=re.MULTILINE)
    
    print json