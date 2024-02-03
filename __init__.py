import os
import requests
import azure.functions as func
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    apiKey = os.environ['BINANCE_API_KEY']
    secretKey = os.environ['BINANCE_API_SECRET']

    # Example: Fetching account information
    url = 'https://api.binance.com/api/v3/account'
    headers = {'X-MBX-APIKEY': apiKey}

    try:
        response = requests.get(url, headers=headers)
        return func.HttpResponse(body=response.text, status_code=response.status_code)
    except Exception as error:
        logging.error(f"Error fetching data from Binance API: {error}")
        return func.HttpResponse("Error fetching data from Binance API", status_code=500)
