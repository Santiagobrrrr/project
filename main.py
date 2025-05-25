from dotenv import load_dotenv
from decimal import Decimal, getcontext
from colorama import Fore, Style
import os
import uuid
import requests
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
# Cargar entorno
load_dotenv()
API_KEY = os.getenv("API_KEY")
AWS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
# Conexión a AWS
db = boto3.resource(
    'dynamodb',
    aws_access_key_id = AWS_KEY,
    aws_secret_access_key = AWS_SECRET,
    region_name = AWS_REGION
)
users_table = db.Table("users")
stocks_table = db.Table("stocks")
symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
# API conexión con JSON TwelveData
def get_prices():
    prices = {}
    for symbol in symbols:
        resp = requests.get(
            f"https://api.twelvedata.com/price?symbol={symbol}&apikey={API_KEY}"
        )
        price_json = resp.json().get("price") if resp.status_code == 200 else None
        prices[symbol] = Decimal(price_json) if price_json else None
    return prices
menu_sis = ""
while menu_sis != "6":
    print(f"{Fore.YELLOW}-----------------------------------------------------{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}        Bienvenido al sistema de inversiones{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}-----------------------------------------------------{Style.RESET_ALL}")
    print(f"{Fore.CYAN}1- Ver acciones{Style.RESET_ALL}")
    print(f"{Fore.CYAN}2- Invertir{Style.RESET_ALL}")
    print(f"{Fore.CYAN}3- Ver portafolio{Style.RESET_ALL}")
    print(f"{Fore.CYAN}4- Registrar usuario{Style.RESET_ALL}")    
    print(f"{Fore.CYAN}5- Reporte general{Style.RESET_ALL}")   
    print(f"{Fore.RED}6- Salir{Style.RESET_ALL}")
    menu_sis = input(f"{Fore.GREEN}\nSeleccione una opción: {Style.RESET_ALL}")
    
    # Ver acciones 
    if menu_sis == "1":
        # Muestra acciones en tiempo real
        prices = get_prices()
        print("\nPrecios actuales:")
        for s, p in prices.items():
            print(f"{s}: ${p:.2f}" if p else f"{s}: No disponible")
    # Invertir
    elif menu_sis == "2":
        # Inicio de sesión de correo 
        email = input("Correo: ")
        user_resp = users_table.get_item(Key={"email": email})
        user = user_resp.get("Item")
        if not user:
            print("Correo no encontrado.")
            continue
        print(f"Hola, {user['name']}")
        # Mostrar acciones y escoger empresa
        prices = get_prices()
        print("Empresas disponibles:")
        for s in symbols:
            print(f"{s}: ${prices[s]:.2f}" if prices[s] else f"{s}: N/A")
        sym = input("Seleccione símbolo: ").upper()
        price = prices.get(sym)
        if not price:
            print("Símbolo inválido o sin precio.")
            continue
        # Total a invertir
        amt = Decimal(input("Monto a invertir: $"))
        if amt > user['balance']:
            print("Fondos insuficientes.")
            continue
        # Calcular acciones
        shares = amt / price
        # Actualizar saldo
        new_balance = user['balance'] - amt
        users_table.update_item(
            Key={"email": email},
            UpdateExpression="SET balance = :b",
            ExpressionAttributeValues={":b": new_balance}
        )
        # Registrar o acumular inversión usando scan
        investment_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        stocks_table.put_item(Item={
            "email": email,
            "investment_id": investment_id,  # Clave única
            "symbol": sym,
            "shares": str(shares),
            "price_per_share": str(price),
            "timestamp": now
        })
        print("Inversión registrada con éxito.")

    # Ver portafolio
    elif menu_sis == "3":
        email = input("Correo: ")
        user_resp = users_table.get_item(Key={"email": email})
        user = user_resp.get("Item")
        if not user:
            print("Correo no encontrado.")
            continue
        print(f"Usuario: {user['name']}")
        print(f"Saldo disponible: ${user['balance']:.2f}")
        # Obtener todas inversiones con scan
        inv_resp = stocks_table.scan(
            FilterExpression=Attr("email").eq(email)
        )
        invs = inv_resp.get('Items', [])
        if not invs:
            print("No hay inversiones registradas.")
            continue
        prices = get_prices()
        total_gain = Decimal('0')
        print("\nHistorial de inversiones:")
        for it in invs:
            sym = it['symbol']
            shares = Decimal(it.get('shares', '0'))
            bought_price = Decimal(it.get('price_per_share', '0'))
            current_price = prices.get(sym) or Decimal('0')
            invested = shares * bought_price
            current_value = shares * current_price
            gain = current_value - invested
            total_gain += gain
            price_disp = f"${current_price:.2f}" if current_price else "N/A"
            date = it.get('timestamp', 'Sin fecha')
            print(f"- {sym} ({date}): invertido ${invested:.2f} a ${bought_price:.2f}, G/P ${gain:.2f}")
        print(f"Ganancia/Pérdida total acumulada: ${total_gain:.2f}")
        
    # Registrar usuario
    elif menu_sis == "4":
        name = input("Nombre: ")
        email = input("Correo: ")
        while True: 
            entrada = input("Saldo Inicial: $")
            try:
                bal = Decimal(entrada)
                break
            except:
                print("Porfavor, ingrese un número válido (solo digitos).")
        # Revisar si ya existe
        existing = users_table.get_item(Key={"email": email})
        if "Item" in existing:
            print("Este correo ya está registrado.")
            continue

        users_table.put_item(Item={
            "email": email,
            "name": name,
            "balance": bal,
            "userId": str(uuid.uuid4())
        })
        print(f"Usuario registrado con éxito.")
        
    # Reporte general
    elif menu_sis == "5":
        email = input("Correo: ")
        user_resp = users_table.get_item(Key={"email": email})
        user = user_resp.get("Item")
        if not user:
            print("Correo no encontrado.")
            continue
        print(f"\nResumen General de Portafolio")
        print(f"----------------------------------")
        print(f"Usuario: {user['name']}")
        print(f"Saldo disponible: ${user['balance']:.2f}")
        
        inv_resp = stocks_table.scan(
            FilterExpression=Attr("email").eq(email)
        )
        invs = inv_resp.get('Items', [])
        if not invs:
            print("No hay inversiones registradas.")
            continue

        prices = get_prices()
        total_invested = Decimal('0')
        total_actual_value = Decimal('0')
        total_gain = Decimal('0')
        count = 0

        print(f"\nInversiones:")
        for it in invs:
            sym = it['symbol']
            shares = Decimal(it.get('shares', '0'))
            bought_price = Decimal(it.get('price_per_share', '0'))
            current_price = prices.get(sym) or Decimal('0')
            invested = shares * bought_price
            current_value = shares * current_price
            gain = current_value - invested

            total_invested += invested
            total_actual_value += current_value
            total_gain += gain
            count += 1

            print(f"- {sym}: {shares:.2f} acciones, comprado a ${bought_price:.2f}, ahora ${current_price:.2f}, G/P: ${gain:.2f}")

        print(f"\nValor total invertido: ${total_invested:.2f}")
        print(f"Valor actual del portafolio: ${total_actual_value:.2f}")
        print(f"Ganancia/Pérdida total: ${total_gain:.2f}")
        print(f"Total de inversiones realizadas: {count}")
        
    # Salir del sistema    
    elif menu_sis == "6":
        print(f"Salio del sistema, nos vemos.")
        
    else:
        print(f"Ingreso invalido, intente nuevamente")