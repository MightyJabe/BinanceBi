import os
import hashlib
import hmac
import time
import requests
import azure.functions as func
import logging
from urllib.parse import urlencode

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="main")
def main(req: func.HttpRequest) -> func.HttpResponse:
    apiKey = os.environ['BINANCE_API_KEY']
    secretKey = os.environ['BINANCE_API_SECRET'].encode()

    # Example: Fetching account information
    url = 'https://fapi.binance.com/fapi/v2/account'

    # Generate a timestamp in milliseconds
    timestamp = int(time.time() * 1000)

    # Create a dictionary of parameters, including the timestamp
    # You may include other parameters as required by your request
    params = {'timestamp': timestamp}

    # Encode parameters and create a signature
    query_string = urlencode(params)
    signature = hmac.new(secretKey, query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    # Append signature to the parameters
    params['signature'] = signature

    # Set up the headers with your API key
    headers = {
        'X-MBX-APIKEY': apiKey,
    }

    try:
        # Send a GET request with the headers and parameters
        response = requests.get(url, headers=headers, params=params)
        return func.HttpResponse(body=response.text, status_code=response.status_code)
    except Exception as error:
        logging.error(f"Error fetching data from Binance API: {error}")
        return func.HttpResponse("Error fetching data from Binance API", status_code=500)
