import boto3
import urllib2

region = 'eu-central-1'
s3bucket = 'cf-templates-195j3qxly0wxh-eu-central-1'  # where to store the cf template
git_url = 'https://raw.githubusercontent.com/pkazmierczak/aws-cloudformation-templates/master/csgo.yaml'
stackname = 'killing'
hostedzone = 'piotrkazmierczak.com.'
key = 'piotrkazmierczak'
gslt = '15F60ECD8DFA7B28C8AD9C4D06135AB8'


def handle(event, context):

    cf = boto3.client('cloudformation', region_name=region)

    if event['action'] == 'start':
        s3 = boto3.client('s3', region_name=region)
        response = urllib2.urlopen(git_url)
        s3.upload_fileobj(response, s3bucket, 'csgo.yaml')

        cf.create_stack(
            StackName=stackname,
            TemplateURL='https://s3.eu-central-1.amazonaws.com/' + s3bucket + '/csgo.yaml',
            Parameters=[
                {
                    'ParameterKey': 'HostedZone',
                    'ParameterValue': hostedzone
                },
                {
                    'ParameterKey': 'KeyName',
                    'ParameterValue': key
                },
                {
                    'ParameterKey': 'GSLT',
                    'ParameterValue': gslt
                }])

        print 'creating csgo server'
    else:
        cf.delete_stack(StackName='killing')
        print 'terminating csgo server'
