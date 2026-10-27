import requests
import time

url = "http://172.30.80.245/capture"

print("RailGuard automatic camera capture started")
print("Press Ctrl+C to stop")

count = 0

try:
    while True:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            count += 1

            filename = f"capture_{count}.jpg"

            with open(filename, "wb") as file:
                file.write(response.content)

            print(f"✅ Image {count} captured")

        else:
            print("❌ Capture failed:", response.status_code)

        time.sleep(2)

except KeyboardInterrupt:
    print("\n🛑 Capture stopped")