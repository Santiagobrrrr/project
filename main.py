from app.AWSConnections import AWSConnections
from dotenv import load_dotenv
from decimal import Decimal

import os
import uuid
import time
# Api
import requests
load_dotenv()
api_key = os.getenv("API_KEY")
symbol = 'AAPL'
url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={api_key}"

# Registro de usuario
print("\nBienvenido a tu sistema de inversiones\n")
print("------------------------------------------\n")

name = input("Ingrese su nombre: ")
email = input("Ingrese su correo electrónico: ")
initialBalance = float(input("Ingrese su saldo inicial: $"))

print("\nRegistrando usuario...")
time.sleep(1.5)

userId = str(uuid.uuid4())

print("\nRegistro exitoso!")
print(f"Nombre: {name}")
print(f"Correo Electrónico: {email}")
print(f"Saldo inicial: ${initialBalance:.2f}")
print(f"UUID: {userId}")

# Datos a diccionario
user_data = {
    "user_id": userId,
    "name": name,
    "email": email,
    "initial_balance": Decimal(str(initialBalance))
}

# Conectar a tabla y guardar
aws = AWSConnections()
awsSession = aws.getSession()

def saveUserDynamoDB(session, user):
    try:
        dynamodb = session.resource('dynamodb')
        table = dynamodb.Table('users')  
        table.put_item(Item=user)
        print("\nRegistrado correctamente.")
    except Exception as e:
        print("\nError al registrarse", e)

saveUserDynamoDB(awsSession, user_data)