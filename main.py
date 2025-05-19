from app.AWSConnections import AWSConnections

aws = AWSConnections()
awsSession = aws.getSession()

def saveUserDynamoDB(session, user):
  dynamodb = session.resource('dynamodb')
  table = dynamodb.Table('users')
  response = table.put_item(Item=user)
  return response

saveUserDynamoDB(awsSession, {"email": "local@local.com", "age": "19", "dpi": "1245155124", "initial_balance": "10000", "name": "Jose Sanchez"})