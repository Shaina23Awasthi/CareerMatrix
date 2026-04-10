import subprocess
import threading
import time
import re

def run_flask():
    subprocess.run(["python", "app.py"])

print("Starting background server...")
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()
time.sleep(3) # wait for flask to come up

print("Creating secure live internet tunnel...")
try:
    with open('live_url.txt', 'w') as f:
        f.write("Fetching live URL...")
        
    process = subprocess.Popen(
        ["ssh", "-o", "StrictHostKeyChecking=no", "-R", "80:localhost:8000", "nokey@localhost.run"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    url = None
    for line in iter(process.stdout.readline, ''):
        print("SSH: ", line.strip())
        if "tunneled with tls termination" in line or ".lhr.life" in line:
            match = re.search(r'https://[a-zA-Z0-9-]+\.lhr\.life', line)
            if match:
                url = match.group(0)
                print(f"\n===> LIVE URL READY: {url} <===\n")
                with open('live_url.txt', 'w') as f:
                    f.write(url)
                break
        
except Exception as e:
    print(f"Error: {e}")
