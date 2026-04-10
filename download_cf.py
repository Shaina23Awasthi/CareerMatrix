import urllib.request
import ssl

print("Downloading cloudflared executable...")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
urllib.request.urlretrieve(url, "cloudflared.exe", context=ctx)
print("Downloaded successfully!")
