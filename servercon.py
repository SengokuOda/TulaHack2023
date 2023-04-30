import requests

url = 'https://unik-server.site/'
filename = 'photo.png'

with open(filename, 'rb') as f:
    files = {'photo': f}
    response = requests.post(url, files=files)

print(response.status_code) # Печатаем статус-код ответа от сервера
