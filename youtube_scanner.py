import requests

WEBHOOK_URL = "https://stock-scanner-production-dd80.up.railway.app/api/webhook-update"

def send_scanner_data():
    stock_data = {
        "symbol": "DICE",
        "name": "سهم دايس للصناعات النسيجية",
        "price": "2.05",
        "signal": "إشارة إيجابية قوية",
        "source": "YouTube Scanner Bot"
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=stock_data)
        print(f"تم الإرسال بنجاح: {response.status_code}")
    except Exception as e:
        print(f"خطأ في الاتصال: {e}")

if __name__ == "__main__":
    send_scanner_data()
