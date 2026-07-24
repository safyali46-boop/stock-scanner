import os
import requests

# رابط السيرفر بتاعك على ريلواي
WEBHOOK_URL = "https://stock-scanner-production-dd80.up.railway.app/api/webhook-update"

def fetch_channel_stocks():
    # هنا هنربط جلب أحدث تحليلات قنوات أركان وزيندو
    # كمثال توضيحي للربط الفعلي مع التطبيق:
    stocks_found = [
        {"symbol": "ARKAN_PICK", "name": "تحليل قناة أركان", "price": "متابعة", "signal": "إشارة جديدة من القناة", "source": "قناة أركان"},
        {"symbol": "ZENDO_PICK", "name": "تحليل قناة زيندو", "price": "متابعة", "signal": "فرصة مقترحة", "source": "قناة زيندو"}
    ]
    
    for stock in stocks_found:
        try:
            response = requests.post(WEBHOOK_URL, json=stock)
            print(f"تم إرسال سهم {stock['symbol']}: {response.status_code}")
        except Exception as e:
            print(f"خطأ في الإرسال: {e}")

if __name__ == "__main__":
    fetch_channel_stocks()
