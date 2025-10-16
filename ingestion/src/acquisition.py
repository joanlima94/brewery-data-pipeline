import requests 
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import json

url_metadata = 'https://api.openbrewerydb.org/v1/breweries/meta'

req = requests.get(url=url_metadata)
total_breweries = req.json()['total']

breweries_per_page = 200

bronze_path = f"{os.getcwd()}/medallion/bronze/{datetime.now(ZoneInfo('America/Sao_Paulo')).date()}"
os.makedirs(bronze_path, exist_ok=True)

def get_breweries_list(page, per_page=200) -> list:
    breweries_list_url = f"https://api.openbrewerydb.org/v1/breweries?page={page}&per_page={per_page}"

    req_b = requests.get(url=breweries_list_url)
    req_b.raise_for_status()
    return req_b.json()

total_pages = (total_breweries // breweries_per_page) + (1 if total_breweries % breweries_per_page else 0)

for page in range(1, total_pages + 1):
    print(f"Baixando página {page} de {total_pages}...")
    data = get_breweries_list(page, breweries_per_page)
    
    file_path = os.path.join(bronze_path, f"page_{page:04d}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Download concluído. Arquivos salvos em: {bronze_path}")