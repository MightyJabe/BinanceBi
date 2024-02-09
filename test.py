import os
import pyodbc
import azure.functions as func

def get_db_connection():
    server = os.environ["DB_SERVER"]
    database = os.environ["DB_NAME"]
    username = os.environ["DB_USER"]
    password = os.environ["DB_PASS"]
    driver= '{ODBC Driver 17 for SQL Server}'
    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    cnxn = pyodbc.connect(connection_string)
    return cnxn

def main(req: func.HttpRequest) -> func.HttpResponse:
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
