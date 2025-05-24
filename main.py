from dotenv import load_dotenv
from decimal import Decimal
from colorama import Fore, Style

import os
import uuid
import requests
import boto3

# Cargar API 
load_dotenv()
apiKey = os.getenv("API_KEY")

if not apiKey:
    print(f"{Fore.RED}Error: No se encontró una API Key válida. Verifica tu archivo .env.{Style.RESET_ALL}")
    exit()

# Configuraracion AWS
awsAccessKey = os.getenv("AWS_ACCESS_KEY")
awsSecretKey = os.getenv("AWS_SECRET_KEY")
awsRegion = os.getenv("AWS_REGION")

# inicio secion aws
awsSession = boto3.Session(
    aws_access_key_id=awsAccessKey,
    aws_secret_access_key=awsSecretKey,
    region_name=awsRegion
)

dynamoDb = awsSession.resource('dynamodb')
stocksTable = dynamoDb.Table('stocks')

# las empresas (si quieren pueden poner otras)
symbolsList = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

# precios de las acciones
def getStockPrices(symbols):
    stockData = {}
    for symbol in symbols:
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={apiKey}"
        response = requests.get(url)
        
        if response.status_code == 200:
            price = response.json().get("price")
            if price:
                stockData[symbol] = Decimal(price)
            else:
                stockData[symbol] = None
        else:
            stockData[symbol] = None
    
    return stockData

# Registro de usuario
print(f"{Fore.MAGENTA}\nBienvenido a tu sistema de inversiones{Style.RESET_ALL}")
print(f"-----------------------------------------------------")

userName = input(f"{Fore.BLUE}Ingrese su nombre:{Style.RESET_ALL} ")
userEmail = input(f"{Fore.GREEN}Ingrese su correo electrónico:{Style.RESET_ALL} ")

# saldo en nums
while True:
    try:
        initialBalance = Decimal(input(f"{Fore.RED}Ingrese su saldo inicial {Fore.RED}(solo números :D):{Style.RESET_ALL} $"))
        break  
    except ValueError:
        print(f"{Fore.RED}Error: Solo se pueden ingresar números. Inténtelo de nuevo.{Style.RESET_ALL}")

userId = str(uuid.uuid4())

# Info de registro
print(f"{Fore.GREEN}\nRegistro exitoso!{Style.RESET_ALL}")
print(f"{Fore.YELLOW}Nombre:{Style.RESET_ALL} {userName}")
print(f"{Fore.GREEN}Correo Electrónico:{Style.RESET_ALL} {userEmail}")
print(f"{Fore.CYAN}Saldo inicial:{Style.RESET_ALL} ${initialBalance:.2f}")
print(f"{Fore.MAGENTA}UUID:{Style.RESET_ALL} {userId}")

# Guardar información inicial en DynamoDB
userData = {
    "userId": userId,
    "userName": userName,
    "email": userEmail,  
    "balance": initialBalance,
    "investments": {}
}

def saveToDynamoDb(data):
    try:
        stocksTable.put_item(Item=data)
        print("\nDatos guardados correctamente en DynamoDB.")
    except Exception as error:
        print("\nError al guardar datos en DynamoDB:", error)

saveToDynamoDb(userData)

# sistema de inversion
totalSpent = Decimal("0")

while True:
    # Mostrar precios de empresas (si quiere seguir inviertiendo)
    stockPrices = getStockPrices(symbolsList)
    print("\nPrecios actuales de empresas:")
    for symbol, price in stockPrices.items():
        if price:
            print(f"{Fore.YELLOW}{symbol}:{Style.RESET_ALL} ${price:.2f}")
        else:
            print(f"{Fore.YELLOW}{symbol}:{Style.RESET_ALL} Error al obtener precio")
    print(f"{Fore.GREEN}Saldo restante: ${initialBalance:.2f}{Style.RESET_ALL}")

    #seleccionar otra empresa
    print(f"\n{Fore.CYAN}Seleccione la empresa donde desea invertir (o 'salir' para terminar):{Style.RESET_ALL}")
    selectedSymbol = input("Empresa: ").upper()

    if selectedSymbol == "SALIR":
        break
    if selectedSymbol not in stockPrices or stockPrices[selectedSymbol] is None:
        print(f"{Fore.RED}Símbolo inválido o error en la cotización.{Style.RESET_ALL}")
        continue

    # precio de la acción
    pricePerShare = stockPrices[selectedSymbol]

    try:
        #numero de acciones a comprar
        sharesCount = int(input(f"{Fore.MAGENTA}Ingrese cuántas veces quiere invertir en {selectedSymbol} (cada inversión equivale al precio de una acción):{Style.RESET_ALL} "))

        # Calcular costo total
        totalCost = sharesCount * pricePerShare

        if totalCost > initialBalance:
            print(f"{Fore.RED}Fondos insuficientes para comprar {sharesCount} acciones de {selectedSymbol}.{Style.RESET_ALL}")
            continue

        # Registrar inversión
        if selectedSymbol in userData["investments"]:
            userData["investments"][selectedSymbol] += sharesCount
        else:
            userData["investments"][selectedSymbol] = sharesCount

        # Actualizar saldo y gasto total
        initialBalance -= totalCost
        totalSpent += totalCost
        userData["balance"] = initialBalance

        print(f"{Fore.GREEN}Compra exitosa! Adquiriste {sharesCount} acciones de {selectedSymbol}.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Saldo restante: ${initialBalance:.2f}{Style.RESET_ALL}")

        # Guardar actualización en la tabla de DynamoDB
        saveToDynamoDb(userData)

    except ValueError:
        print(f"{Fore.RED}Número inválido. Ingrese un valor entero válido.{Style.RESET_ALL}")

# resumen total de la inversion
print("\n--------------------------------------------")
print(f"{Fore.YELLOW}RESUMEN DE INVERSIÓN:{Style.RESET_ALL}")
print(f"{Fore.CYAN}Saldo restante: ${initialBalance:.2f}{Style.RESET_ALL}")
print(f"{Fore.RED}Total invertido: ${totalSpent:.2f}{Style.RESET_ALL}")
print(f"{Fore.MAGENTA}Inversiones realizadas:{Style.RESET_ALL}")

for symbol, shares in userData["investments"].items():
    pricePerShare = stockPrices[symbol]
    cost = shares * pricePerShare
    print(f"{Fore.YELLOW}- {symbol}:{Style.RESET_ALL} {shares} acciones (${cost:.2f})")
    
print("\nGracias por usar el sistema de inversiones. ¡Hasta la próxima!")
print("--------------------------------------------")

#no se q mas ponerle
#ola
#chejo.dlg en insta 