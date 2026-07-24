import requests
import json

WEBHOOK_URL = "https://stock-scanner-production-dd80.up.railway.app/api/webhook-update"

def process_video_transcript():
    stock = {
        "symbol": "DICE",
        "name": "سهم دايس للصناعات النسيجية",
        "price": "2.05",
        "demand": "قوي",
        "supply": "متوسط",
        "liquidity": "عالية",
        "analysis": "تحديث تلقائي من البوت",
        "news": "يعمل بنجاح",
        "market": "EGX",
        "source": "Auto Scanner Bot"
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=stock)
        print(f"تم إرسال السهم بنجاح، الحالة: {response.status_code}")
    except Exception as e:
        print(f"خطأ في الاتصال: {e}")

if __name__ == "__main__":
    process_video_transcript()
