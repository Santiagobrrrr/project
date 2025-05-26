# Proyecto Final - Pensamiento Computacional
Este programa o sistema de inversiones, permite ver acciones en tiempo real sobre las empresas de Apple, Microsoft, Google, Amazon, Tesla.
En las cuales el usuario puede invertir en acciones una cantidad de dinero, este dinero es el dinero que se le pide al momento de registrarse, sobre cuanto saldo virtual pondrá en su cuenta o en el sistema de inversiones, también podrá ver su portafolio, y su saldo actual, en el cual mirará su historial de inversiones. Por último podrá ver un resumen o un reporte general de su cuenta.
Estos datos serán guardados en tablas de AWS con DynamoDB.

## Es necesario:

1. Clonar repositorio
   ```bash
   git clone https://github.com/Santiagobrrrr/project.git

2. Crear entorno virtual
   ```bash
    python -m venv venv
    - Para mac:
    source venv/bin/activate   # En Windows: venv\Scripts\activate


3. Instalar librerías
   ```bash
     pip install -r requirements.txt

4. Tener las configuraciones
    - Descomprimir #credenciales.zip
    - Cortar y pegar los archivos .env y /aws en la carpeta donde fue clonado el repositorio (PARA QUE ESTE TERMINE DE HACER SU CONEXIÓN)

Se le pedira siempre el email para loguearlo y ver su historial