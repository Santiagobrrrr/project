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

menu_opt = ""
while menu_opt != "5":
    print(f"{Fore.YELLOW}-----------------------------------------------------{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}        Bienvenido al sistema de inversiones{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}-----------------------------------------------------{Style.RESET_ALL}")
    print(f"{Fore.CYAN}1- Ver acciones{Style.RESET_ALL}")
    print(f"{Fore.CYAN}2- Invertir{Style.RESET_ALL}")
    print(f"{Fore.CYAN}3- Ver portafolio{Style.RESET_ALL}")
    print(f"{Fore.CYAN}4- Registrar usuario{Style.RESET_ALL}")
    print(f"{Fore.RED}5- Salir{Style.RESET_ALL}")
    menu_opt = input(f"{Fore.GREEN}\nSeleccione una opción: {Style.RESET_ALL}")
    
    # Ver acciones 
    if menu_opt == "1":
        # Muestra acciones en tiempo real
        prices = get_prices()
        print("\nPrecios actuales:")
        for s, p in prices.items():
            print(f"{s}: ${p:.2f}" if p else f"{s}: No disponible")

    # Invertir
    elif menu_opt == "2":
        # Inicio de sesión de correo 
        email = input("Correo: ")
        user_resp = users_table.get_item(Key={"email": email})
        user = user_resp.get("Item")
        if not user:
            print("Correo no encontrado.")
            continue
        print(f"Hola, {user['name']}")
        # Mostrar acciones
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
        scan_resp = stocks_table.scan(
            FilterExpression=Attr("email").eq(email) & Attr("symbol").eq(sym)
        )
        items = scan_resp.get('Items', [])
        now = datetime.utcnow().isoformat()
        if items:
            inv = items[0]
            prev_shares = Decimal(inv.get('shares', '0'))
            prev_price = Decimal(inv.get('price_per_share', '0'))
            total_shares = prev_shares + shares
            avg_price = ((prev_price * prev_shares) + (price * shares)) / total_shares
            stocks_table.put_item(Item={
                "email": email,
                "symbol": sym,
                "shares": str(total_shares),
                "price_per_share": str(avg_price),
                "timestamp": now
            })
        else:
            stocks_table.put_item(Item={
                "email": email,
                "symbol": sym,
                "shares": str(shares),
                "price_per_share": str(price),
                "timestamp": now
            })
        print("Inversión registrada con éxito.")

    # Ver portafolio
    elif menu_opt == "3":
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
            price_disp = f"${current_price:.2f}" if prices.get(sym) else "N/A"
            print(f"- {sym}: inv ${invested:.2f} a ${bought_price:.2f}, act {price_disp}, G/P ${gain:.2f}")
        print(f"Ganancia/Pérdida total acumulada: ${total_gain:.2f}")

    # Registrar usuario
    elif menu_opt == "4":
        name = input("Nombre: ")
        email = input("Correo: ")
       
        while True: 
            entrada = input("Saldo Inicial: $")
            try:
                bal = Decimal(entrada)
                break
            except:
                print("Porfavor, ingrese un número válido (solo digitos).")
        

    elif menu_opt == "5":
        print("Salio del sistema, nos vemos.")
    else:
        print("Opción inválida.")
