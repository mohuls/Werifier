import requests

url = 'https://werifier.com/email/update/'
myobj = {'samplekey': 'samplevalue'}

x = requests.post(url, data = myobj)

f = open('/home/ubuntu/Werifier/update_email.log', 'a')
f.write('\n')
f.write(str(x.json()["status"]))
f.close()