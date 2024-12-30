from datetime import datetime

def date_format(data):
    return datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
