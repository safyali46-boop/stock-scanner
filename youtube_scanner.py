import requests

WEBHOOK_URL = "https://stock-scanner-production-dd80.up.railway.app/api/webhook-update"

def fetch_channel_stocks():
    # تحديث بالأسهم الجديدة لقنوات أركان وزيندو
    stocks_found = [
        {"symbol": "ARKAN", "name": "توصية قناة أركان", "price": "متابعة", "signal": "إشارة إيجابية جديدة", "source": "قناة أركان"},
        {"symbol": "ZENDO", "name": "توصية قناة زيندو", "price": "متابعة", "signal": "فرصة مقترحة بالسوق", "source": "قناة زيندو"}
    ]
    
    for stock in stocks_found:
        try:
            response = requests.post(WEBHOOK_URL, json=stock)
            print(f"تم إرسال سهم {stock['symbol']}: {response.status_code}")
        except Exception as e:
            print(f"خطأ في الإرسال: {e}")

if __name__ == "__main__":
    fetch_channel_stocks()
