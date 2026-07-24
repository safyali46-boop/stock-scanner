from flask import Flask, jsonify, request, render_template_string
import os

app = Flask(__name__)

scanner_live_signals = [
    {
        "source": "Auto Scanner", 
        "symbol": "NVDA", 
        "name": "إنيديا", 
        "price": "130.20", 
        "demand": "50K", 
        "supply": "20K", 
        "liquidity": "عالية جداً", 
        "analysis": "اختراق قمة الجلسة وطلب مؤسسي قوي.",
        "news": "إنيديا تعلن عن رقائق جديدة بمعمارية متطورة.",
        "market": "US"
    }
]

all_assets_database = [
    {"symbol": "NVDA", "name": "إنيديا", "price": "130.20", "demand": "50K", "supply": "20K", "liquidity": "عالية جداً", "analysis": "اختراق قمة الجلسة وطلب مؤسسي قوي.", "news": "إنيديا تعلن عن رقائق جديدة وسط طلب قياسي.", "market": "US"},
    {"symbol": "AAPL", "name": "آبل", "price": "185.50", "demand": "80K", "supply": "30K", "liquidity": "عالية جداً", "analysis": "ثبات أعلى الدعم مع ضغط شرایی مؤسسي.", "news": "آبل تسجل إيرادات فصلية قياسية.", "market": "US"},
    {"symbol": "DICE", "name": "دايس للصناعات", "price": "2.05", "demand": "15K", "supply": "5K", "liquidity": "متوسطة", "analysis": "نشاط ملحوظ بالسوق المصري وعروض شراء عند مستويات الدعم.", "news": "تداولات نشطة على سهم دايس وسط ترقب لنتائج الأعمال.", "market": "EG"},
    {"symbol": "COMI", "name": "البنك التجاري الدولي", "price": "80.00", "demand": "120K", "supply": "40K", "liquidity": "عالية جداً", "analysis": "اتجاه صاعد واستقرار للسيولة المؤسسية.", "news": "البنك يعلن عن توزيعات نقدية مرتقبة.", "market": "EG"},
    {"symbol": "EURUSD", "name": "اليورو دولار", "price": "1.0850", "demand": "100K", "supply": "90K", "liquidity": "عالية", "analysis": "تذبذب عرضي حول مستويات الدعم مع سيولة متوازنة.", "news": "الأسواق تترقب بيانات التضخم الأمريكية.", "market": "Forex"},
    {"symbol": "GBPUSD", "name": "السترليني دولار", "price": "1.2650", "demand": "80K", "supply": "70K", "liquidity": "عالية", "analysis": "ثبات أعلى مستويات الدعم الرئيسية للفنيات.", "news": "تطورات اقتصادية هامة تؤثر على زوج الاسترليني.", "market": "Forex"}
]

INDEX_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة التداول المتكاملة</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; direction: rtl; }
        .container { max-width: 1100px; margin: auto; background: #1e293b; padding: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        h1 { text-align: center; color: #38bdf8; font-size: 24px; margin-bottom: 5px; }
        p.subtitle { text-align: center; color: #94a3b8; font-size: 14px; margin-top: 0; }
        
        .search-box { margin: 20px 0; text-align: center; }
        .search-box input { width: 100%; max-width: 500px; padding: 12px; font-size: 16px; background: #0f172a; color: #fff; border: 1px solid #334155; border-radius: 8px; outline: none; }

        .nav-tabs { display: flex; gap: 10px; margin-bottom: 20px; justify-content: center; flex-wrap: wrap; }
        .tab-btn { background: #334155; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 15px; font-weight: bold; transition: 0.3s; }
        .tab-btn.active, .tab-btn:hover { background: #0284c7; }

        .section-content { display: none; }
        .section-content.active { display: block; }

        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; border: 1px solid #334155; text-align: center; font-size: 13px; cursor: pointer; }
        th { background-color: #0f172a; color: #38bdf8; cursor: default; }
        tr:hover { background-color: #334155; }
        .badge { background: #0284c7; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
        
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.7); justify-content: center; align-items: center; }
        .modal-content { background-color: #1e293b; padding: 25px; border-radius: 10px; width: 500px; max-width: 90%; border: 1px solid #334155; text-align: right; }
        .close-btn { background: #ef4444; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; float: left; font-weight: bold; }
        .card { background: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #334155; margin-top: 10px; cursor: pointer; transition: 0.2s; }
        .card:hover { border-color: #38bdf8; }
    </style>
</head>
<body>

<div class="container">
    <h1>منصة التداول المتكاملة</h1>
    <p class="subtitle">السكنر اللحظي، الأسهم، والعملات مع محرك البحث الشامل</p>
    
    <div class="search-box">
        <input type="text" id="globalSearch" placeholder="ابحث برمز العملة أو السهم (مثال: EURUSD, دايس, COMI)..." oninput="filterData()">
    </div>

    <div class="nav-tabs">
        <button class="tab-btn active" onclick="switchTab('scanner', this)">📡 السكنر اللحظي</button>
        <button class="tab-btn" onclick="switchTab('us-stocks', this)">🇺🇸 والأسهم المصرية والعالمية</button>
        <button class="tab-btn" onclick="switchTab('currencies', this)">💱 العملات والسيولة</button>
    </div>

    <div id="scanner" class="section-content active">
        <h3 style="color: #38bdf8;">إشارات السكنر اللحظي (تحديث آلي)</h3>
        <table>
            <thead>
                <tr>
                    <th>المصدر</th>
                    <th>الرمز</th>
                    <th>الاسم / العملة</th>
                    <th>السعر</th>
                    <th>الطلب</th>
                    <th>العرض</th>
                    <th>السيولة</th>
                    <th>التحليل السريع</th>
                </tr>
            </thead>
            <tbody id="scannerTableBody"></tbody>
        </table>
    </div>

    <div id="us-stocks" class="section-content">
        <h3 style="color: #38bdf8;">قائمة الأسهم والشروط المعتمدة</h3>
        <div id="stocksList"></div>
    </div>

    <div id="currencies" class="section-content">
        <h3 style="color: #38bdf8;">متابعة العملات والأسواق العالمية</h3>
        <div id="forexList"></div>
    </div>

</div>

<div id="stockModal" class="modal">
    <div class="modal-content">
        <button class="close-btn" onclick="closeModal()">إغلاق</button>
        <h2 id="modalSymbol" style="color: #38bdf8; margin-top: 0;"></h2>
        <p><b>الاسم / الرمز:</b> <span id="modalName"></span> | <b>السعر:</b> <span id="modalPrice"></span></p>
        <hr style="border-color: #334155;">
        <h3 style="color: #22c55e; font-size: 16px;">الطلب والعرض والسيولة:</h3>
        <p id="modalSupplyDemand" style="color: #f8fafc; font-size: 14px;"></p>
        <h3 style="color: #22c55e; font-size: 16px;">أحدث الأخبار والتقارير:</h3>
        <p id="modalNews" style="color: #94a3b8; font-size: 14px; line-height: 1.5;"></p>
        <h3 style="color: #38bdf8; font-size: 16px;">التحليل الفني والشروط:</h3>
        <p id="modalAnalysis" style="color: #f8fafc; font-size: 14px; line-height: 1.5;"></p>
    </div>
</div>

<script>
    let scannerData = [];
    let assetsData = [];

    function switchTab(tabId, btn) {
        document.querySelectorAll('.section-content').forEach(el => el.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
        btn.classList.add('active');
    }

    async function fetchAppData() {
        try {
            const response = await fetch('/api/app-data');
            const data = await response.json();
            scannerData = data.scanner;
            assetsData = data.assets;

            renderScanner(scannerData);
            renderAssets(assetsData);
        } catch (error) {
            console.error('خطأ في جلب البيانات:', error);
        }
    }

    function renderScanner(data) {
        const tbody = document.getElementById('scannerTableBody');
        tbody.innerHTML = '';
        if(!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8">لا توجد نتائج مطابقة في السكنر...</td></tr>';
            return;
        }
        data.forEach((item) => {
            tbody.innerHTML += `<tr onclick='openModal(${JSON.stringify(item)})'>
                <td><span class="badge">${item.source || 'Scanner'}</span></td>
                <td><b>${item.symbol}</b></td>
                <td>${item.name}</td>
                <td>${item.price}</td>
                <td style="color: #22c55e;">${item.demand}</td>
                <td style="color: #ef4444;">${item.supply}</td>
                <td><b>${item.liquidity}</b></td>
                <td>${item.analysis}</td>
            </tr>`;
        });
    }

    function renderAssets(data) {
        const stocksDiv = document.getElementById('stocksList');
        const forexDiv = document.getElementById('forexList');
        stocksDiv.innerHTML = '<h4 style="color: #22c55e; margin-top:0;">الأسهم المتاحة:</h4>';
        forexDiv.innerHTML = '<h4 style="color: #22c55e; margin-top:0;">أزواج العملات:</h4>';

        let hasStocks = false;
        let hasForex = false;

        if(!data || data.length === 0) {
            stocksDiv.innerHTML += '<p style="color: #94a3b8;">لا توجد نتائج...</p>';
            forexDiv.innerHTML += '<p style="color: #94a3b8;">لا توجد نتائج...</p>';
            return;
        }

        data.forEach((item) => {
            const cardHTML = `<div class="card" onclick='openModal(${JSON.stringify(item)})'>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <b style="color: #38bdf8; font-size: 16px;">${item.symbol} - ${item.name}</b>
                    <span class="badge">السعر: ${item.price}</span>
                </div>
                <p style="color: #94a3b8; font-size: 13px; margin: 8px 0 0 0;"><b>التحليل:</b> ${item.analysis}</p>
            </div>`;

            if (item.market === 'Forex') {
                forexDiv.innerHTML += cardHTML;
                hasForex = true;
            } else {
                stocksDiv.innerHTML += cardHTML;
                hasStocks = true;
            }
        });

        if (!hasStocks) stocksDiv.innerHTML += '<p style="color: #94a3b8;">لا توجد أسهم مطابقة للبحث.</p>';
        if (!hasForex) forexDiv.innerHTML += '<p style="color: #94a3b8;">لا توجد عملات مطابقة للبحث.</p>';
    }

    function filterData() {
        const query = document.getElementById('globalSearch').value.toLowerCase().trim();
        if (!query) {
            renderScanner(scannerData);
            renderAssets(assetsData);
            return;
        }
        const filteredScanner = scannerData.filter(item => 
            (item.symbol && item.symbol.toLowerCase().includes(query)) || 
            (item.name && item.name.toLowerCase().includes(query))
        );
        const filteredAssets = assetsData.filter(item => 
            (item.symbol && item.symbol.toLowerCase().includes(query)) || 
            (item.name && item.name.toLowerCase().includes(query)) ||
            (item.market && item.market.toLowerCase().includes(query))
        );
        renderScanner(filteredScanner);
        renderAssets(filteredAssets);
    }

    function openModal(item) {
        document.getElementById('modalSymbol').innerText = item.symbol;
        document.getElementById('modalName').innerText = item.name;
        document.getElementById('modalPrice').innerText = item.price;
        document.getElementById('modalSupplyDemand').innerHTML = `حجم الطلب: <span style="color: #22c55e;">${item.demand || 'N/A'}</span> | حجم العرض: <span style="color: #ef4444;">${item.supply || 'N/A'}</span> | السيولة: <b>${item.liquidity || 'عادية'}</b>`;
        document.getElementById('modalNews').innerText = item.news || "لا توجد أخبار عاجلة مسجلة لهذا الأصل.";
        document.getElementById('modalAnalysis').innerText = item.analysis || "تحت الفحص وفقاً لشروط السوق والسيولة.";
        document.getElementById('stockModal').style.display = 'flex';
    }

    function closeModal() {
        document.getElementById('stockModal').style.display = 'none';
    }

    setInterval(fetchAppData, 3000);
    fetchAppData();
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(INDEX_HTML)

@app.route('/api/app-data', methods=['GET'])
def get_app_data():
    return jsonify({
        "scanner": scanner_live_signals,
        "assets": all_assets_database
    })

@app.route('/api/webhook-update', methods=['POST'])
def webhook_update():
    incoming_data = request.json
    if incoming_data:
        new_item = {
            "source": incoming_data.get("source", "Auto Scanner"),
            "symbol": incoming_data.get("symbol", "N/A"),
            "name": incoming_data.get("name", "غير محدد"),
            "price": incoming_data.get("price", "0.00"),
            "demand": incoming_data.get("demand", "0"),
            "supply": incoming_data.get("supply", "0"),
            "liquidity": incoming_data.get("liquidity", "عادية"),
            "analysis": incoming_data.get("analysis", "تحديث آلي مباشر"),
            "news": incoming_data.get("news", "أخبار فورية مرصودة."),
            "market": incoming_data.get("market", "US")
        }
        scanner_live_signals.append(new_item)
        if not any(a['symbol'] == new_item['symbol'] for a in all_assets_database):
            all_assets_database.append(new_item)
            
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
