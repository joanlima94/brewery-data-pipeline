import requests
import json
import logging
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = "https://api.openbrewerydb.org/v1"
BREWERIES_PER_PAGE = 200

def get_total_breweries() -> int:
    try:
        url = f"{API_BASE_URL}/breweries/meta"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['total']
    
    except requests.RequestException as e:
        logger.error(f"Error fetching total breweries: {e}")
        raise
    except requests.Timeout:
        logger.error("Request timed out while fetching total breweries")
        raise
    except requests.ConnectionError:
        logger.error("Connection error occurred while fetching total breweries")
        raise

def get_breweries_page(page: int, per_page: int = BREWERIES_PER_PAGE) -> List[dict]:
    try:
        url = f"{API_BASE_URL}/breweries?page={page}&per_page={per_page}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    
    except requests.RequestException as e:
        logger.error(f"Error fetching breweries page {page}: {e}")
        raise
    except requests.Timeout:
        logger.error(f"Request timed out while fetching breweries page {page}")
        raise
    except requests.ConnectionError:
        logger.error(f"Connection error occurred while fetching breweries page {page}")
        raise

def save_page_to_bronze(data: List[dict], page: int, base_path: Path):
    file_path = base_path / f"page_{page:02d}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    today = datetime.now(ZoneInfo('America/Sao_Paulo')).date()
    data_root = os.getenv("DATA_OUTPUT_ROOT", "/app/data")
    bronze_path = f"{Path(data_root)}/medallion/bronze/breweries/{str(today)}"
    bronze_path.mkdir(parents=True, exist_ok=True)

    total = get_total_breweries()
    total_pages = (total // BREWERIES_PER_PAGE) + (1 if total % BREWERIES_PER_PAGE else 0)

    for page in range(1, total_pages + 1):
        logger.info(f"Downloading {page} from {total_pages}")
        data = get_breweries_page(page)
        save_page_to_bronze(data, page, bronze_path)

    logger.info(f"Download completed. Files saved in: {bronze_path}")

if __name__ == "__main__":
    main()