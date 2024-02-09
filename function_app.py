import os
import hashlib
import hmac
import time
import requests
import azure.functions as func
import logging
from urllib.parse import urlencode
import pyodbc

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Centralize the API key and secret retrieval
apiKey = os.environ['BINANCE_API_KEY']
secretKey = os.environ['BINANCE_API_SECRET'].encode()

def generate_params():
    timestamp = int(time.time() * 1000)
    params = {'timestamp': timestamp}
    query_string = urlencode(params)
    signature = hmac.new(secretKey, query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    params['signature'] = signature
    return params

# Function to send a request to the Binance API and handle the response
def send_request(url, params):
    headers = {'X-MBX-APIKEY': apiKey}
    try:
        response = requests.get(url, headers=headers, params=params)
        return func.HttpResponse(body=response.text, status_code=response.status_code)
    except Exception as error:
        logging.error(f"Error fetching data from Binance API: {error}")
        return func.HttpResponse("Error fetching data from Binance API", status_code=500)
    
@app.route(route="account_info")
def account_info(req: func.HttpRequest) -> func.HttpResponse:
    # Endpoint for fetching account information
    url = 'https://fapi.binance.com/fapi/v2/account'
    params = generate_params()
    return send_request(url, params)

@app.route(route="trade_history")
def trade_history(req: func.HttpRequest) -> func.HttpResponse:
    # Retrieve symbol and limit from the request query parameters
    symbol = req.params.get('symbol')
    limit = req.params.get('limit')  # Example default limit
    # Endpoint for fetching user's trade history
    url = 'https://fapi.binance.com/fapi/v1/userTrades'
    params = generate_params()
    # Add specific parameters for the trade history request
    if symbol:
        params.update({'symbol': symbol, 'limit': limit})
    return send_request(url, params)


def get_db_connection():
    server = os.environ["DB_SERVER"]
    database = os.environ["DB_NAME"]
    username = os.environ["DB_USER"]
    password = os.environ["DB_PASS"]
    driver= '{ODBC Driver 17 for SQL Server}'
    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    cnxn = pyodbc.connect(connection_string)
    return cnxn
@app.route(route="test_db")
def test_db(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cnxn = get_db_connection()
        cursor = cnxn.cursor()
        # Simple query to test the connection
        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        if row:
            return func.HttpResponse(f"Database connection successful. DB Version: {row[0]}", status_code=200)
        else:
            return func.HttpResponse("Failed to query database version.", status_code=500)
    except Exception as e:
        return func.HttpResponse(f"Database connection failed: {str(e)}", status_code=500)