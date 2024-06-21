import requests 

#Made by Lizzie Moratti 
#This script is intended to be ran from an EC2 instance using Amazon Linux 2. It can be adapted for other purposes.
#By default (as of time of writing 11/25/2022), AL2 has python 2.7 supported and already has the requests library imported.
def requestsWrapper( headers, url,HTTPmethod='GET'):
    print(headers,url,HTTPmethod)
    if(HTTPmethod == 'PUT'):
        response = requests.put(url, headers=headers).text
        return response
    response = response = requests.get(url, headers=headers).text
    return response

# IMDSv2 Metadata token
#curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"
try:
    token = requestsWrapper('http://169.254.169.254/latest/api/token', {'X-aws-ec2-metadata-token-ttl-seconds': '21600',},'PUT')
except:
    print("We were unable to get the token needed for IMDVs2")
#getting the role name
try:
    headers = {'X-aws-ec2-metadata-token': '%s' % token,} #formatted using Python 2.7 compatible methods
    ec2role = requests.get('http://169.254.169.254/latest/meta-data/iam/security-credentials/', headers=headers).text
except:
    print("Something went wrong trying to get the EC2 instance role name. Are you sure one is attached?")
#security credentials
# curl -H "X-aws-ec2-metadata-token: $TOKEN" -v http://169.254.169.254/latest/meta-data/iam/security-credentials/role-name/
try:
    headers = {'X-aws-ec2-metadata-token': '%s' % token,} #formatted using Python 2.7 compatible methods
    credentials = requests.get('http://169.254.169.254/latest/meta-data/iam/security-credentials/%s/' % ec2role, headers=headers).text
    print(credentials)
except:
    print("Something went wrong gathering the security-credentials.")