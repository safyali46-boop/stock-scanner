import requests

WEBHOOK_URL = "https://stock-scanner-production-dd80.up.railway.app/api/webhook-update"

def fetch_channel_stocks():
    # البيانات الأصلية (الاسكنر وسهم دايس)
    stocks_found = [
        {
            "symbol": "DICE", 
            "name": "دايس للملابس الجاهزة", 
            "price": "2.05", 
            "signal": "شراء / متابعة", 
            "source": "الاسكنر العام"
        },
        {
            "symbol": "SCANNER", 
            "name": "إيدو اسكنر السوق", 
            "price": "مباشر", 
            "signal": "تحديث إيجابي", 
            "source": "إيدو اسكنر"
        }
    ]
    
    for stock in stocks_found:
        try:
            response = requests.post(WEBHOOK_URL, json=stock)
            print(f"تم إرسال سهم {stock['symbol']}: {response.status_code}")
        except Exception as e:
            print(f"خطأ في الإرسال: {e}")

if __name__ == "__main__":
    fetch_channel_stocks()
