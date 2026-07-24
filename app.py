from flask import Flask, jsonify, request, render_template_string
import os

app = Flask(__name__)

INDEX_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arcane & Zendoo Live Audio Scanner</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; direction: rtl; }
        .container { max-width: 1050px; margin: auto; background: #1e293b; padding: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        h1 { text-align: center; color: #38bdf8; font-size: 24px; margin-bottom: 5px; }
        p.subtitle { text-align: center; color: #94a3b8; font-size: 14px; margin-top: 0; }
        .filters { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        input, select { padding: 10px; font-size: 16px; background: #0f172a; color: #fff; border: 1px solid #334155; border-radius: 6px; flex: 1; min-width: 200px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; border: 1px solid #334155; text-align: center; font-size: 14px; }
        th { background-color: #0f172a; color: #38bdf8; }
        .positive { color: #22c55e; font-weight: bold; }
        .badge { background: #0284c7; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
        .source-tag { background: #8b5cf6; color: white; padding: 3px 6px; border-radius: 4px; font-size: 11px; }
        .audio-btn { background: #22c55e; color: #fff; border: none; padding: 10px 15px; border-radius: 6px; cursor: pointer; font-weight: bold; }
        .audio-btn:hover { background: #16a34a; }
    </style>
</head>
<body>

<div class="container">
    <h1>السكنر الصوتي الموحد (Arcane + Zendoo + TradingView)</h1>
    <p class="subtitle">تتبع الزخم اللحظي مع التنبيه الصوتي التلقائي</p>
    
    <div class="filters">
        <select id="marketSelect" onchange="loadData()">
            <option value="ALL">جميع المصادر والأسواق</option>
            <option value="US">السوق الأمريكية (Zendoo & Arcane)</option>
            <option value="TV">توصيات TradingView</option>
        </select>
        <input type="text" id="searchInput" placeholder="ابحث برمز السهم (مثلاً NVDA, TSLA, DICE)..." oninput="loadData()">
        <button class="audio-btn" onclick="testVoice()">🔊 اختبار الصوت</button>
    </div>

    <table>
        <thead>
            <tr>
                <th>المصدر</th>
                <th>الرمز</th>
                <th>اسم السهم</th>
                <th>السعر</th>
                <th>التغير</th>
                <th>الحالة / الزخم</th>
                <th>التحليل الفني والطلبات</th>
            </tr>
        </thead>
        <tbody id="tableBody">
            <!-- سيتم تحميل البيانات هنا -->
        </tbody>
    </table>
</div>

<script>
    function speakStock(symbol, name) {
        if ('speechSynthesis' in window) {
            const text = `تنبيه سهم ${name}, الرمز ${symbol}`;
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'ar-SA';
            utterance.rate = 1.0;
            window.speechSynthesis.speak(utterance);
        }
    }

    function testVoice() {
        speakStock("NVDA", "إنيديا");
    }

    async function loadData() {
        const market = document.getElementById('marketSelect').value;
        const query = document.getElementById('searchInput').value.trim();
        
        try {
            const response = await fetch(`/api/market?market=${encodeURIComponent(market)}&q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';
            
            if(!data || data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7">لا توجد نتائج مطابقة</td></tr>';
                return;
            }

            data.forEach((item) => {
                const row = `<tr>
                    <td><span class="source-tag">${item.source}</span></td>
                    <td><b>${item.symbol}</b></td>
                    <td>${item.name}</td>
                    <td>${item.price}</td>
                    <td class="positive">+${item.change}%</td>
                    <td><span class="badge">${item.momentum}</span></td>
                    <td>${item.analysis} <button style="margin-right:5px; background:none; border:none; cursor:pointer;" onclick="speakStock('${item.symbol}', '${item.name}')" title="انطق اسم السهم">🔊</button></td>
                </tr>`;
                tbody.innerHTML += row;
            });

        } catch (error) {
            console.error('خطأ في جلب البيانات:', error);
        }
    }

    loadData();
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(INDEX_HTML)

@app.route('/api/market')
def market_data():
    market = request.args.get('market', 'ALL')
    query = request.args.get('q', '').lower().strip()
    
    all_data = [
        {"source": "Zendoo", "symbol": "NVDA", "name": "إنيديا", "price": "128.50", "change": "5.1", "momentum": "High Volume Gapper", "analysis": "اختراق قمة الجلسة مع طلبات قوية"},
        {"source": "Arcane Monitor", "symbol": "TSLA", "name": "تسلا", "price": "224.20", "change": "4.3", "momentum": "Momentum Breakout", "analysis": "تدفق سيولة لحظية وعروض شراء متلاحقة"},
        {"source": "TradingView", "symbol": "AAPL", "name": "أبل", "price": "184.10", "change": "2.0", "momentum": "Bullish Cross", "analysis": "تقاطع إيجابي للمؤشرات الفنية عند الدعم"},
        {"source": "Zendoo", "symbol": "DICE", "name": "دايس للصناعات", "price": "2.05", "change": "3.1", "momentum": "EGX Active", "analysis": "نشاط ملحوظ في السوق المصري وعروض شراء"}
    ]
    
    if market != 'ALL':
        if market == 'US':
            all_data = [x for x in all_data if x['source'] in ['Zendoo', 'Arcane Monitor']]
        elif market == 'TV':
            all_data = [x for x in all_data if x['source'] == 'TradingView']

    if query:
        filtered = [
            item for item in all_data 
            if query in item['symbol'].lower() or query in item['name'].lower()
        ]
    else:
        filtered = all_data
    
    return jsonify(filtered)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
