import requests 

url_metadata = 'https://api.openbrewerydb.org/v1/breweries/meta'

req = requests.get(url=url_metadata)
total_breweries = req.json()['total']
breweries_per_page = 200

print(total_breweries % breweries_per_page)