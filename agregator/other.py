# import requests

# url = ('https://newsapi.org/v2/everything?'
#        'q=Газпром&'
#        'from=2025-05-30&'
#        'sortBy=popularity&'
#        'apiKey=b99923eb48a44f2d86601b131276c98a')

# response = requests.get(url)

# print(response.json())


import http.client, urllib.parse

conn = http.client.HTTPConnection('api.mediastack.com')

params = urllib.parse.urlencode({
    'access_key': '1173ec150bb3bfcf99c44d8201b796ea',
    'search': 'Газпром',
    'countries': 'ru',
    })

conn.request('GET', '/v1/news?{}'.format(params))

res = conn.getresponse()
data = res.read()

print(data.decode('utf-8'))