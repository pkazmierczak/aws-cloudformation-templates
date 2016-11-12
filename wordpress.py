# This is a *fast* HA Wordpress template. It uses an
# SQL-on-EC2 instead of RDS for faster deployment and it
# automatically installs Wordpress using wp-cli.

from troposphere import Base64, GetAtt, Join, Output
from troposphere import Parameter, Ref, Tags, Template

import troposphere.ec2 as ec2
import troposphere.cloudwatch as cloudwatch
import troposphere.autoscaling as autoscaling
import troposphere.elasticloadbalancing as elb
import troposphere.route53 as route53
from troposphere.policies import (CreationPolicy, UpdatePolicy,
                                  AutoScalingRollingUpdate, ResourceSignal)

import constants as const

t = Template()

t.add_version("2010-09-09")

t.add_description("Basic WP stack")

# PARAMETERS

Project = t.add_parameter(Parameter(
    "Project",
    Type="String",
    Description="Project-Name",
    Default="Project-Name",
    MinLength="1",
    MaxLength="255",
    AllowedPattern=const.ASCII_CHAR,
    ConstraintDescription=const.INVALID_ASCII_MSG,
))

Company = t.add_parameter(Parameter(
    "Company",
    Type="String",
    Description="Company-Name",
    Default="Company-Name",
    MinLength="1",
    MaxLength="255",
    AllowedPattern=const.ASCII_CHAR,
    ConstraintDescription=const.INVALID_ASCII_MSG,
))

Domain = t.add_parameter(Parameter(
    "Domain",
    Type="String",
    Default="lab.cloudreach.co.uk",
    Description=const.VALID_DNS_REGEX,
    # AllowedPattern=const.VALID_DNS_REGEX
)
)

PublicSubnet1 = t.add_parameter(Parameter(
    "PublicSubnet1",
    Default="10.0.0.0/24",
    Type="String",
    Description="Address range for a public subnet to be created in AZ1.",
))

PublicSubnet2 = t.add_parameter(Parameter(
    "PublicSubnet2",
    Default="10.0.2.0/24",
    Type="String",
    Description="Address range for a public subnet to be created in AZ2.",
))

PrivateSubnet1 = t.add_parameter(Parameter(
    "PrivateSubnet1",
    Default="10.0.1.0/24",
    Type="String",
    Description="Address range for a private subnet to be created in AZ1.",
))

PrivateSubnet2 = t.add_parameter(Parameter(
    "PrivateSubnet2",
    Default="10.0.3.0/24",
    Type="String",
    Description="Address range for a private subnet to be created in AZ2.",
))

VpcCidr = t.add_parameter(Parameter(
    "VpcCidr",
    Default="10.0.0.0/16",
    Type="String",
    Description="CIDR address for the VPC to be created.",
))

KeyName = t.add_parameter(Parameter(
    "KeyName",
    ConstraintDescription="must be the name of an existing EC2 KeyPair.",
    Type="AWS::EC2::KeyPair::KeyName",
    Default="showroom",
    Description="Name of an existing EC2 KeyPair to enable SSH access to the instances",
))

AvailabilityZone1 = t.add_parameter(Parameter(
    "AvailabilityZone1",
    Default="eu-central-1a",
    Type="String",
    Description="First AZ to use for PublicSubnet1/PrivateSubnet1.",
))

AvailabilityZone2 = t.add_parameter(Parameter(
    "AvailabilityZone2",
    Default="eu-central-1b",
    Type="String",
    Description="Second AZ to use for PublicSubnet2/PrivateSubnet2.",
))

InstanceType = t.add_parameter(Parameter(
    "InstanceType",
    Default="t2.micro",
    ConstraintDescription="must be a valid EC2 instance type.",
    Type="String",
    Description="Instance type for NAT nodes.",
    AllowedValues=["t2.micro", "t2.medium", "m3.medium", "m3.large", "m3.xlarge", "m3.2xlarge"],
))

WebServerCapacity = t.add_parameter(Parameter(
    "WebServerCapacity",
    Description="The initial nuber of WebServer instances",
    Default="2",
    Type="Number",
    MaxValue="5",
    MinValue="1",
    ConstraintDescription="must be between 1 and 5 EC2 instances.",
))

# MAPPINGS

t.add_mapping("AWSRegion2AMI", const.UBUNTU_14_AMI)

# RESOURCES

# DNSZone = t.add_resource(route53.HostedZone(
#     "DNSZone",
#     Name=Ref(Domain),
#     HostedZoneConfig=route53.HostedZoneConfiguration(
#         Comment=Join("-", ["hosted zone for ", Ref(Domain)]),
#     ),
# ))

PublicRoute = t.add_resource(ec2.Route(
    "PublicRoute",
    GatewayId=Ref("InternetGateway"),
    DestinationCidrBlock="0.0.0.0/0",
    RouteTableId=Ref("PublicRouteTable"),
))

InternetGateway = t.add_resource(ec2.InternetGateway(
    "InternetGateway",
    Tags=Tags(
        Application=Ref("AWS::StackName"),
        Network="Public",
        Name=Join("-", ["IGW", Ref(Project)]),
    ),
))

PubSubnet1RTAssoc = t.add_resource(ec2.SubnetRouteTableAssociation(
    "PubSubnet1RTAssoc",
    SubnetId=Ref("PubSubnet1"),
    RouteTableId=Ref("PublicRouteTable"),
))

GatewayToInternet = t.add_resource(ec2.VPCGatewayAttachment(
    "GatewayToInternet",
    VpcId=Ref("VPC"),
    InternetGatewayId=Ref(InternetGateway),
))

VPC = t.add_resource(ec2.VPC(
    "VPC",
    CidrBlock=Ref(VpcCidr),
    Tags=Tags(
        Name=Join("-", ["VPC", Ref(Project)]),
        Application=Ref("AWS::StackName"),
        Network="Public",
    ),
))

PubSubnet2RTAssoc = t.add_resource(ec2.SubnetRouteTableAssociation(
    "PubSubnet2RTAssoc",
    SubnetId=Ref("PubSubnet2"),
    RouteTableId=Ref("PublicRouteTable"),
))

PublicRouteTable = t.add_resource(ec2.RouteTable(
    "PublicRouteTable",
    VpcId=Ref(VPC),
    Tags=Tags(
        Application=Ref("AWS::StackName"),
        Network="Public",
        Name=Join("-", ["RT-PU-1", Ref(Project)]),
    ),
))

PubSubnet1 = t.add_resource(ec2.Subnet(
    "PubSubnet1",
    Tags=Tags(
        Application=Ref("AWS::StackName"),
        Network="Public",
        Name=Join("-", ["NT-PU-1", Ref(Project)]),
    ),
    VpcId=Ref(VPC),
    CidrBlock=Ref(PublicSubnet1),
    AvailabilityZone=Ref(AvailabilityZone1),
    MapPublicIpOnLaunch=True,
))

PubSubnet2 = t.add_resource(ec2.Subnet(
    "PubSubnet2",
    Tags=Tags(
        Application=Ref("AWS::StackName"),
        Network="Public",
        Name=Join("-", ["NT-PU-2", Ref(Project)]),
    ),
    VpcId=Ref(VPC),
    CidrBlock=Ref(PublicSubnet2),
    AvailabilityZone=Ref(AvailabilityZone2),
    MapPublicIpOnLaunch=True,
))

PriSubnet1 = t.add_resource(ec2.Subnet(
    "PriSubnet1",
    Tags=Tags(
        Application=Ref("AWS::StackName"),
        Network="Private",
        Name=Join("-", ["NT-PR-1", Ref(Project)]),
    ),
    VpcId=Ref("VPC"),
    CidrBlock=Ref(PrivateSubnet1),
    AvailabilityZone=Ref(AvailabilityZone1),
))

PrivateRouteTable1 = t.add_resource(ec2.RouteTable(
    "PrivateRouteTable1",
    VpcId=Ref("VPC"),
    Tags=Tags(
        Application=Ref("AWS::StackName"),
        Network="Private",
        Name=Join("-", ["RT-PR-1", Ref(Project)]),
    ),
))

PriSubnet1RTAssoc = t.add_resource(ec2.SubnetRouteTableAssociation(
    "PriSubnet1RTAssoc",
    SubnetId=Ref(PriSubnet1),
    RouteTableId=Ref(PrivateRouteTable1),
))

LoadbalancerSecurityGroup = t.add_resource(ec2.SecurityGroup(
    "LoadbalancerSecurityGroup",
    SecurityGroupIngress=[
        {"ToPort": "443", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "443"},
        {"ToPort": "80", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "80"}],
    VpcId=Ref(VPC),
    GroupDescription="Enable HTTP access via port 80 and 443 access",
    Tags=Tags(
        Name=Join("-", ["SG-ELB", Ref(Project)]),
    ),
))

WebServerHTTPAllowELB = t.add_resource(ec2.SecurityGroupIngress(
    "WebServerHTTPAllowELB",
    ToPort="80",
    IpProtocol="tcp",
    SourceSecurityGroupId=Ref(LoadbalancerSecurityGroup),
    GroupId=Ref("WebServerSecurityGroup"),
    FromPort="80",
))

WebServerSecurityGroup = t.add_resource(ec2.SecurityGroup(
    "WebServerSecurityGroup",
    SecurityGroupIngress=[
        {"ToPort": "80", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "80"},
        {"ToPort": "22", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "22"}],
    VpcId=Ref(VPC),
    GroupDescription="Enable HTTP access via port 80 and SSH access",
    Tags=Tags(
        Name=Join("-", ["SG-WEB", Ref(Project)]),
    ),
))

DBEC2SecurityGroup = t.add_resource(ec2.SecurityGroup(
    "DBEC2SecurityGroup",
    SecurityGroupIngress=[
        {"ToPort": "3306", "IpProtocol": "tcp", "CidrIp": Ref(PublicSubnet1), "FromPort": "3306"},
        {"ToPort": "3306", "IpProtocol": "tcp", "CidrIp": Ref(PublicSubnet2), "FromPort": "3306"}],
    VpcId=Ref(VPC),
    GroupDescription="Open database for access",
    Tags=Tags(
        Name=Join("-", ["SG-DB", Ref(Project)]),
    ),
))

Database = t.add_resource(ec2.Instance(
    "Database",
    Tags=Tags(
        Name=Join("-", ["DB", Ref(Project)]),
    ),
    ImageId="ami-f125399d",
    SubnetId=Ref(PriSubnet1),
    KeyName=Ref(KeyName),
    SecurityGroupIds=[Ref(DBEC2SecurityGroup)],
    InstanceType=Ref(InstanceType)
))

metadata = {
    "AWS::CloudFormation::Init": {
        "configSets": {
            "wordpress_install": [
                "install_wordpress"]
        },
        "install_wordpress": {
            "packages": {
                "apt": {
                    "apache2": [],
                    "php5": [],
                    "php5-mysql": [],
                    "mysql-client": [],
                    "sendmail": []
                }
            },
            "sources": {
                "/var/www/html": "http://wordpress.org/latest.tar.gz"
            },
            "files": {
                "/tmp/create-wp-config": {
                    "content": {
                        "Fn::Join": ["", [
                            "#!/bin/bash\n",
                            "cp /var/www/html/wordpress/wp-config-sample.php /var/www/html/wordpress/wp-config.php\n",
                            "sed -i \"s/'database_name_here'/'wordpress'/g\" wp-config.php\n",
                            "sed -i \"s/'username_here'/'root'/g\" wp-config.php\n",
                            "sed -i \"s/'password_here'/'wordpress'/g\" wp-config.php\n",
                            "sed -i \"s/'localhost'/'",
                            {
                                "Fn::GetAtt": [
                                    "Database",
                                    "PrivateIp"
                                ]
                            },
                            "'/g\" wp-config.php\n"
                        ]
                        ]
                    },
                    "mode": "000500",
                    "owner": "root",
                    "group": "root"
                }
            },
            "commands": {
                "01_configure_wordpress": {
                    "command": "/tmp/create-wp-config",
                    "cwd": "/var/www/html/wordpress"
                }
            }
        }
    }
}

WebServerLaunchConfiguration = t.add_resource(autoscaling.LaunchConfiguration(
    "WebServerLaunchConfiguration",
    DependsOn=["PubSubnet1RTAssoc", "PubSubnet2RTAssoc", "Database"],
    Metadata=metadata,
    UserData=Base64(Join("", [
        "#!/bin/bash -x\n",
        "exec > /tmp/userdata.log 2>&1\n",
        "/usr/local/bin/cfn-init -v ",
        "         --stack ",
        {
            "Ref": "AWS::StackName"
        },
        "         --resource WebServerLaunchConfiguration ",
        "         --configsets wordpress_install ",
        "         --region ",
        {
            "Ref": "AWS::Region"
        },
        "\n",
        "/bin/mv /var/www/html/wordpress/* /var/www/html/\n",
        "/bin/rm -f /var/www/html/index.html\n",
        "/bin/rm -rf /var/www/html/wordpress/\n",
        "/usr/sbin/service apache2 restart\n",
        "/usr/bin/curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar\n",
        "/bin/chmod +x wp-cli.phar\n",
        "/bin/mv wp-cli.phar /usr/local/bin/wp\n",
        "cd /var/www/html/ && sudo -u www-data /usr/local/bin/wp core install ",
        "--url='", {"Ref": "ELBcname"}, "' ",
        "--title='", {"Ref": "Project"}, "' ",
        "--admin_user='root' ",
        "--admin_password='wordpress' ",
        "--admin_email='wordpress@piotr.lab.cloudreach.co.uk'\n",
        "/usr/local/bin/cfn-signal -e $? ",
        "         --stack ",
        {
            "Ref": "AWS::StackName"
        },
        "         --resource WebServerAutoScalingGroup ",
        "         --region ",
        {
            "Ref": "AWS::Region"
        },
        "\n"
    ]
    )),
    ImageId="ami-91233ffd",  # eu-central-1
    # ImageId="ami-bc8ad2cb",  # eu-west-1
    KeyName=Ref(KeyName),
    SecurityGroups=[Ref(WebServerSecurityGroup)],
    InstanceType=Ref(InstanceType),
    AssociatePublicIpAddress=True,
))

WebServerAutoScalingGroup = t.add_resource(autoscaling.AutoScalingGroup(
    "WebServerAutoScalingGroup",
    MinSize=Ref(WebServerCapacity),
    MaxSize="5",
    VPCZoneIdentifier=[Ref(PubSubnet1), Ref(PubSubnet2)],
    AvailabilityZones=[Ref(AvailabilityZone1), Ref(AvailabilityZone2)],
    Tags=autoscaling.Tags(
        Name=Join("-", ["WEB-ASG", Ref(Project)]),
    ),
    LoadBalancerNames=[Ref("ElasticLoadBalancer")],
    LaunchConfigurationName=Ref("WebServerLaunchConfiguration"),
    CreationPolicy=CreationPolicy(
        ResourceSignal=ResourceSignal(
            Count=1,
            Timeout='PT10M'
        )),
    UpdatePolicy=UpdatePolicy(
        AutoScalingRollingUpdate=AutoScalingRollingUpdate(
            PauseTime='PT5M',
            MinInstancesInService="1",
            MaxBatchSize='1',
            WaitOnResourceSignals=True
        )
    )
))

WebServerScaleUpPolicy = t.add_resource(autoscaling.ScalingPolicy(
    "WebServerScaleUpPolicy",
    ScalingAdjustment="1",
    Cooldown="60",
    AutoScalingGroupName=Ref(WebServerAutoScalingGroup),
    AdjustmentType="ChangeInCapacity",
))

WebServerScaleDownPolicy = t.add_resource(autoscaling.ScalingPolicy(
    "WebServerScaleDownPolicy",
    ScalingAdjustment="-1",
    Cooldown="60",
    AutoScalingGroupName=Ref(WebServerAutoScalingGroup),
    AdjustmentType="ChangeInCapacity",
))

CPUAlarmLow = t.add_resource(cloudwatch.Alarm(
    "CPUAlarmLow",
    EvaluationPeriods="2",
    Dimensions=[
        cloudwatch.MetricDimension(
            Name="AutoScalingGroupName",
            Value=Ref("WebServerAutoScalingGroup")
        ),
    ],
    AlarmActions=[Ref("WebServerScaleDownPolicy")],
    AlarmDescription="Scale-down if CPU < 70% for 1 minute",
    Namespace="AWS/EC2",
    Period="60",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold="70",
    MetricName="CPUUtilization",
))

CPUAlarmHigh = t.add_resource(cloudwatch.Alarm(
    "CPUAlarmHigh",
    EvaluationPeriods="2",
    Dimensions=[
        cloudwatch.MetricDimension(
            Name="AutoScalingGroupName",
            Value=Ref("WebServerAutoScalingGroup")
        ),
    ],
    AlarmActions=[Ref(WebServerScaleUpPolicy)],
    AlarmDescription="Scale-up if CPU > 50% for 1 minute",
    Namespace="AWS/EC2",
    Period="60",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold="50",
    MetricName="CPUUtilization",
))

# WaitHandle = t.add_resource(cloudformation.WaitConditionHandle(
#     "WaitHandle",
# ))

# WaitCondition = t.add_resource(cloudformation.WaitCondition(
#     "WaitCondition",
#     Handle=Ref("WaitHandle"),
#     Timeout="600",
#     DependsOn="WebServerAutoScalingGroup",
# ))

ElasticLoadBalancer = t.add_resource(elb.LoadBalancer(
    "ElasticLoadBalancer",
    DependsOn=["InternetGateway", "GatewayToInternet"],
    Subnets=[Ref(PubSubnet1), Ref(PubSubnet2)],
    Listeners=[{"InstancePort": "80", "LoadBalancerPort": "80", "Protocol": "HTTP"}],
    CrossZone="true",
    SecurityGroups=[Ref(LoadbalancerSecurityGroup)],
    HealthCheck=elb.HealthCheck(
        HealthyThreshold="3",
        Interval="5",
        Target="HTTP:80/",
        Timeout="2",
        UnhealthyThreshold="5",
    ),
))

ELBcname = t.add_resource(route53.RecordSetType(
    "ELBcname",
    DependsOn=["InternetGateway", "GatewayToInternet"],
    # HostedZoneName=Join("", [Ref(Domain), "."]),
    HostedZoneId="ZTUOGS2NQKC92",
    Comment="CNAME to Web ELB",
    Name=Join("", [Ref(Project), ".showroom.", Ref(Domain)]),
    Type="CNAME",
    TTL="900",
    ResourceRecords=[GetAtt(ElasticLoadBalancer, "DNSName")]
))

#  OUTPUTS

VPCID = t.add_output(Output(
    "VPCID",
    Description="VPC Info.",
    Value=Join("", [Ref(VPC), " (", Ref(VpcCidr), ")"]),
))

PublicSubnet1 = t.add_output(Output(
    "PublicSubnet1",
    Description="Public Subnet #1.",
    Value=Join("", [Ref(PubSubnet1), " (", Ref(PublicSubnet1), ") ", Ref(AvailabilityZone1)]),
))

PublicSubnet2 = t.add_output(Output(
    "PublicSubnet2",
    Description="Public Subnet #2.",
    Value=Join("", [Ref(PubSubnet2), " (", Ref(PublicSubnet2), ") ", Ref(AvailabilityZone2)]),
))

PublicRouteTable = t.add_output(Output(
    "PublicRouteTable",
    Description="Public Route Table.",
    Value=Join("", [Ref(PublicRouteTable), " (0.0.0.0/0 -> ", Ref(InternetGateway), ")"]),
))

WebServerSecurityGroupID = t.add_output(Output(
    "WebServerSecurityGroupID",
    Description="WebServerSecurityGroupID",
    Value=Join("", [Ref(WebServerSecurityGroup)]),
))

LoadbalancerSecurityGroupID = t.add_output(Output(
    "LoadbalancerSecurityGroupID",
    Description="LoadbalancerSecurityGroupID",
    Value=Join("", [Ref(LoadbalancerSecurityGroup)]),
))

ELBurl = t.add_output(Output(
    "ELBurl",
    Description="URL of ELB",
    Value=Join("", ["http://", GetAtt(ElasticLoadBalancer, "DNSName")]),
))

print(t.to_json())
