from app.AWSConnections import AWSConnections
from dotenv import load_dotenv
from decimal import Decimal
from colorama import Fore, Style

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
print("--------------------------------------------\n")

name = input("Ingrese su nombre: ")
email = input("Ingrese su correo electrónico: ")
initialBalance = float(input("Ingrese su saldo inicial: $"))

userId = str(uuid.uuid4())

print(f"{Fore.RED}\nRegistro exitoso!{Style.RESET_ALL}")
print(f"{Fore.YELLOW}Nombre:{Style.RESET_ALL} {name}")
print(f"{Fore.GREEN}Correo Electrónico:{Style.RESET_ALL} {email}")
print(f"{Fore.CYAN}Saldo inicial:{Style.RESET_ALL} ${initialBalance:.2f}")
print(f"{Fore.MAGENTA}UUID:{Style.RESET_ALL} {userId}")

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

def saveUserDynamoDB(session, stock):
    try:    
        dynamodb = session.resource('dynamodb')
        table = dynamodb.Table('stocks')  
        table.put_item(Item=stock)
        print("\nRegistrado correctamente.")
    except Exception as e:
        print("\nError al registrarse", e)

saveUserDynamoDB(awsSession, user_data)

def saveUserDynamoDB(session, stock):
    try:
        dynamodb = session.resource('dynamodb')
        table = dynamodb.Table('stocks')  
        table.put_item(Item=stock)
        print("\nRegistrado correctamente.")
    except Exception as e:
        print("\nError al registrarse", e)