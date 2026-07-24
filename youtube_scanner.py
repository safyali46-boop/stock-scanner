import requests

WEBHOOK_URL = "https://stock-scanner-production-dd80.up.railway.app/api/webhook-update"

def fetch_smallcaps_stocks():
    # أسهم ومؤشرات Small Caps الأمريكية المستخرجة من تحليلات القنوات
    stocks_found = [
        {
            "symbol": "ARKAN_SC", 
            "name": "Arkan SmallCap Alert", 
            "price": "Live", 
            "signal": "Breakout / Momentum", 
            "source": "قناة أركان (US SmallCaps)"
        },
        {
            "symbol": "ZENDO_SC", 
            "name": "Zendo SmallCap Watch", 
            "price": "Live", 
            "signal": "High Volume / Runner", 
            "source": "قناة زيندو (US SmallCaps)"
        }
    ]
    
    try:
        # إرسال اللستة كاملة دفعة واحدة بدل سهم سهم
        response = requests.post(WEBHOOK_URL, json=stocks_found)
        print(f"تم إرسال البيانات بنجاح: {response.status_code}")
    except Exception as e:
        print(f"خطأ في الإرسال: {e}")

if __name__ == "__main__":
    fetch_smallcaps_stocks()
