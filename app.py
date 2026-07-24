from flask import Flask, jsonify, request, render_template_string
import os

app = Flask(__name__)

# قاعدة بيانات حية تستقبل التحديثات الآلية من السكنر فوراً
live_scanner_data = [
    {"source": "Auto Scanner Bot", "symbol": "NVDA", "name": "إنيديا", "price": "130.20", "demand": "50K", "supply": "20K", "liquidity": "عالية جداً", "analysis": "رصد آلي: اختراق قمة الجلسة وطلب قوي"}
]

INDEX_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>السكنر الأوتوماتيكي المباشر</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; direction: rtl; }
        .container { max-width: 1100px; margin: auto; background: #1e293b; padding: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        h1 { text-align: center; color: #38bdf8; font-size: 24px; margin-bottom: 5px; }
        p.subtitle { text-align: center; color: #94a3b8; font-size: 14px; margin-top: 0; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; border: 1px solid #334155; text-align: center; font-size: 13px; }
        th { background-color: #0f172a; color: #38bdf8; }
        .badge { background: #0284c7; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
    </style>
</head>
<body>

<div class="container">
    <h1>السكنر الأوتوماتيكي المباشر (تحديث لحظي)</h1>
    <p class="subtitle">الربط الآلي للبث والطلبات مع التنبيه الصوتي</p>
    
    <table>
        <thead>
            <tr>
                <th>المصدر</th>
                <th>الرمز</th>
                <th>اسم السهم</th>
                <th>السعر</th>
                <th>الطلب</th>
                <th>العرض</th>
                <th>السيولة</th>
                <th>التحليل الفني</th>
            </tr>
        </thead>
        <tbody id="tableBody">
            <!-- سيتم تحديث البيانات تلقائياً -->
        </tbody>
    </table>
</div>

<script>
    function speakStock(symbol, name) {
        if ('speechSynthesis' in window) {
            const text = `تنبيه سهم جديد ${name}, الرمز ${symbol}`;
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'ar-SA';
            utterance.rate = 1.0;
            window.speechSynthesis.speak(utterance);
        }
    }

    let lastCount = 0;

    async function fetchLiveScanner() {
        try {
            const response = await fetch('/api/live-data');
            const data = await response.json();
            
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';
            
            if(!data || data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8">في انتظار ورود تحديثات من السكنر...</td></tr>';
                return;
            }

            // إذا دخل سهم جديد، انطقه صوتياً أوتوماتيك
            if (data.length > lastCount && lastCount > 0) {
                const latest = data[data.length - 1];
                speakStock(latest.symbol, latest.name);
            }
            lastCount = data.length;

            data.forEach((item) => {
                const row = `<tr>
                    <td><span class="badge">${item.source}</span></td>
                    <td><b>${item.symbol}</b></td>
                    <td>${item.name}</td>
                    <td>${item.price}</td>
                    <td style="color: #22c55e;">${item.demand}</td>
                    <td style="color: #ef4444;">${item.supply}</td>
                    <td><b>${item.liquidity}</b></td>
                    <td>${item.analysis}</td>
                </tr>`;
                tbody.innerHTML += row;
            });

        } catch (error) {
            console.error('خطأ في الاتصال:', error);
        }
    }

    // تحديث الصفحة أوتوماتيكياً كل 3 ثوانٍ لجلب أحدث إشارات السكنر
    setInterval(fetchLiveScanner, 3000);
    fetchLiveScanner();
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(INDEX_HTML)

@app.route('/api/live-data', methods=['GET'])
def get_live_data():
    return jsonify(live_scanner_data)

# مسار استقبال البيانات الآلي (Webhook) ليتم إرسال الأسهم إليه تلقائياً من نظام السكنر الخارجي
@app.route('/api/webhook-update', methods=['POST'])
def webhook_update():
    incoming_data = request.json
    if incoming_data:
        live_scanner_data.append({
            "source": incoming_data.get("source", "Auto Scanner"),
            "symbol": incoming_data.get("symbol", "N/A"),
            "name": incoming_data.get("name", "غير محدد"),
            "price": incoming_data.get("price", "0.00"),
            "demand": incoming_data.get("demand", "0"),
            "supply": incoming_data.get("supply", "0"),
            "liquidity": incoming_data.get("liquidity", "عادية"),
            "analysis": incoming_data.get("analysis", "تحديث آلي مباشر")
        })
        return jsonify({"status": "success", "message": "تم استقبال وتحديث السهم بنجاح"}), 200
    return jsonify({"status": "error", "message": "بيانات غير صالحة"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
