import os
import hashlib
import hmac
import time
import requests
import azure.functions as func
import logging
from urllib.parse import urlencode

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
    limit = req.params.get('limit', '1000')  # Example default limit
    # Endpoint for fetching user's trade history
    url = 'https://fapi.binance.com/fapi/v1/userTrades'
    params = generate_params()
    # Add specific parameters for the trade history request
    if symbol:
        params.update({'symbol': symbol, 'limit': limit})
    return send_request(url, params)