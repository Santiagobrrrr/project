from app.AWSConnections import AWSConnections

aws = AWSConnections()
awsSession = aws.getSession()

def saveUserDynamoDB(session, user):
  dynamodb = session.resource('dynamodb')
  table = dynamodb.Table('users')
  response = table.put_item(Item=user)
  return response

saveUserDynamoDB(awsSession, {"email": "local@local.com", "age": "19", "dpi": 
"1245155124", "initial_balance": "10000", "name": "Jose Sanchez"})
 
 #Registro de usuario
import uuid
import time

print("\nBienvenido a tu sistema de inversiones\n")
print("------------------------------------------\n")

name = input("Ingrese su nombre: ")
email = input("Ingrese su correo electrónico: ")
initialBalance = float(input("Ingrese su saldo inicial: $"))

print("\nRegistrando usuario...")
time.sleep(1.5)

userId = uuid.uuid4()

print("\nRegistro exitoso!")
print(f"Nombre: {name}")
print(f"Correo Electrónico: {email}")
print(f"Saldo inicial: ${initialBalance:.2f}")
print(f"UUID: {userId}")
