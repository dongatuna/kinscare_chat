import os

def schemafy(data:str):
    _data = data.replace('kinscare_chat.', f"{os.getenv('DB_SCHEMA')}.").replace("table_schema = 'kinscare_chat'", f"table_schema = '{os.getenv('DB_SCHEMA')}'")
    return _data