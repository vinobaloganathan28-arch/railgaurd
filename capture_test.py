import requests

url = "http://172.30.80.245/capture"

response = requests.get(url, timeout=10)

print("Status:", response.status_code)
print("Content-Type:", response.headers.get("Content-Type"))

if response.status_code == 200:
    with open("railguard_test.jpg", "wb") as file:
        file.write(response.content)

    print("✅ Image saved as railguard_test.jpg")
else:
    print("❌ Capture failed")