import requests 
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4IiwiZXhwaXJhdGlvbl9kYXRlIjoxNzcxMTEzNzQ5LjY0MDAyfQ.nLYXwN7W4_rS1GABDEGY-YHUe4ScftdPffY82OpqHNI"
}

requisicao = requests.get("http://127.0.0.1:8000/auth/refresh_token",headers=headers)
print(requisicao)
print(requisicao.json())