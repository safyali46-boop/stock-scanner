from flask import Flask, jsonify, request, render_template_string
import os

app = Flask(__name__)

live_scanner_data = [
    {"source": "Auto Scanner", "symbol": "NVDA", "name": "إنيديا", "price": "130.20", "demand": "50K", "supply": "20K", "liquidity": "عالية جداً", "analysis": "اختراق قمة الجلسة وطلب قوي", "market": "US"},
    {"source": "EGX Live", "symbol": "DICE", "name": "دايس للصناعات", "price": "2.05", "demand": "15K", "supply": "5K", "liquidity": "متوسطة", "analysis": "نشاط السوق المصري وعروض شراء", "market": "EG"},
    {"source": "Forex Bot", "symbol": "EURUSD", "name": "اليورو دولار", "price": "1.0850", "demand": "100K", "supply": "90K", "liquidity": "عالية", "analysis": "تذبذب حول مستويات الدعم", "market": "Forex"}
]

INDEX_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تطبيق التداول الشامل</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; direction: rtl; }
        .container { max-width: 1100px; margin: auto; background: #1e293b; padding: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        h1 { text-align: center; color: #38bdf8; font-size: 24px; margin-bottom: 5px; }
        p.subtitle { text-align: center; color: #94a3b8; font-size: 14px; margin-top: 0; }
        
        /* شريط البحث الموحد */
        .search-box { margin: 20px 0; text-align: center; }
        .search-box input { width: 100%; max-width: 500px; padding: 12px; font-size: 16px; background: #0f172a; color: #fff; border: 1px solid #334155; border-radius: 8px; outline: none; }

        /* شريط التنقل بين الأيقونات */
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
        
        /* نافذة التفاصيل والأخبار */
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.7); justify-content: center; align-items: center; }
        .modal-content { background-color: #1e293b; padding: 25px; border-radius: 10px; width: 500px; max-width: 90%; border: 1px solid #334155; text-align: right; }
        .close-btn { background: #ef4444; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; float: left; font-weight: bold; }
        .card { background: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #334155; margin-top: 10px; }
    </style>
</head>
<body>

<div class="container">
    <h1>منصة التداول المتكاملة</h1>
    <p class="subtitle">السكنر اللحظي، الأسهم الأمريكية والمصرية، والعملات مع البحث المباشر</p>
    
    <!-- خانة البحث الشاملة -->
    <div class="search-box">
        <input type="text" id="globalSearch" placeholder="ابحث برمز السهم، الاسم، أو العملة (مثال: NVDA, دايس, EURUSD)..." oninput="filterData()">
    </div>

    <!-- الأيقونات / الأقسام الرئيسية -->
    <div class="nav-tabs">
        <button class="tab-btn active" onclick="switchTab('scanner', this)">📡 السكنر اللحظي</button>
        <button class="tab-btn" onclick="switchTab('us-stocks', this)">🇺🇸 الأسهم الأمريكية والمصرية</button>
        <button class="tab-btn" onclick="switchTab('currencies', this)">💱 العملات والسيولة</button>
    </div>

    <!-- قسم السكنر اللحظي والبحث العام -->
    <div id="scanner" class="section-content active">
        <h3 style="color: #38bdf8;">إشارات السكنر والأسواق المباشرة</h3>
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
                    <th>التحليل والشروط</th>
                </tr>
            </thead>
            <tbody id="tableBody">
                <!-- البيانات -->
            </tbody>
        </table>
    </div>

    <!-- قسم الشروط والتفاصيل للأسهم -->
    <div id="us-stocks" class="section-content">
        <h3 style="color: #38bdf8;">شروط القبول والتحليل الفني</h3>
        <div class="card">
            <h4 style="color: #22c55e; margin-top:0;">شروط الأسهم الأمريكية والمصرية المعتمدة:</h4>
            <ul style="color: #94a3b8; font-size: 14px; line-height: 1.6;">
                <li>رصد تدفقات السيولة العالية والطلبات المؤسسية اللحظية.</li>
                <li>اختراق مستويات المقاومة الرئيسية أو قمم الجلسة.</li>
                <li>توافق مؤشرات الزخم الملحوظة مع عروض الشراء والبيع.</li>
            </ul>
        </div>
    </div>

    <!-- قسم العملات -->
    <div id="currencies" class="section-content">
        <h3 style="color: #38bdf8;">متابعة العملات والأسواق العالمية</h3>
        <div class="card">
            <p style="color: #94a3b8;">رصد تحركات أزواج العملات الرئيسية وتحديثات السيولة اللحظية المرتبطة بها وشروط التداول الخاصة بها.</p>
        </div>
    </div>

</div>

<!-- نافذة عرض تفاصيل الأخبار والتحليل عند الضغط على السهم -->
<div id="stockModal" class="modal">
    <div class="modal-content">
        <button class="close-btn" onclick="closeModal()">إغلاق</button>
        <h2 id="modalSymbol" style="color: #38bdf8; margin-top: 0;"></h2>
        <p><b>الاسم / الرمز:</b> <span id="modalName"></span></p>
        <hr style="border-color: #334155;">
        <h3 style="color: #22c55e; font-size: 16px;">أحدث الأخبار:</h3>
        <p id="modalNews" style="color: #94a3b8; font-size: 14px;">جاري جلب أحدث الأخبار المرتبطة بالسهم...</p>
        <h3 style="color: #38bdf8; font-size: 16px;">التحليل الفني والشروط:</h3>
        <p id="modalAnalysis" style="color: #f8fafc; font-size: 14px;"></p>
    </div>
</div>

<script>
    let globalData = [];

    function switchTab(tabId, btn) {
        document.querySelectorAll('.section-content').forEach(el => el.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
        btn.classList.add('active');
    }

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
            globalData = await response.json();
            renderTable(globalData);

            if (globalData.length > lastCount && lastCount > 0) {
                const latest = globalData[globalData.length - 1];
                speakStock(latest.symbol, latest.name);
            }
            lastCount = globalData.length;

        } catch (error) {
            console.error('خطأ في الاتصال:', error);
        }
    }

    function renderTable(data) {
        const tbody = document.getElementById('tableBody');
        tbody.innerHTML = '';
        
        if(!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8">لا توجد نتائج مطابقة للبحث...</td></tr>';
            return;
        }

        data.forEach((item) => {
            const row = `<tr onclick='openModal(${JSON.stringify(item)})'>
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
    }

    function filterData() {
        const query = document.getElementById('globalSearch').value.toLowerCase().trim();
        if (!query) {
            renderTable(globalData);
            return;
        }
        const filtered = globalData.filter(item => 
            item.symbol.toLowerCase().includes(query) || 
            item.name.toLowerCase().includes(query)
        );
        renderTable(filtered);
    }

    function openModal(item) {
        document.getElementById('modalSymbol').innerText = item.symbol;
        document.getElementById('modalName').innerText = item.name;
        document.getElementById('modalAnalysis').innerText = item.analysis;
        document.getElementById('modalNews').innerText = "تم رصد تفاعل قوي وأحدث الأخبار المرتبطة بهذا الأصل وفقاً لتحديثات البث اللحظي.";
        document.getElementById('stockModal').style.display = 'flex';
    }

    function closeModal() {
        document.getElementById('stockModal').style.display = 'none';
    }

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
            "analysis": incoming_data.get("analysis", "تحديث آلي مباشر مع الشروط"),
            "market": incoming_data.get("market", "US")
        })
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
