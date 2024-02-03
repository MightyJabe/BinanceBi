import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get('name', 'there')
    return func.HttpResponse(f"Hello {name}!", status_code=200)
