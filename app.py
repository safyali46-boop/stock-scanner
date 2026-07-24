from flask import Flask, jsonify, request, render_template_string, session, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "trading_platform_professional_secret_key"
DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # جدول الأصول والأسهم والسكنر
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            symbol TEXT PRIMARY KEY,
            name TEXT,
            price TEXT,
            demand TEXT,
            supply TEXT,
            liquidity TEXT,
            analysis TEXT,
            news TEXT,
            market TEXT,
            source TEXT
        )
    ''')
    
    # جدول المستخدمين لتسجيل الدخول بالإيميل أو الهاتف + الباسورد
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier TEXT UNIQUE,
            password TEXT
        )
    ''')
    
    # حساب افتراضي اولي للتجربة (يمكنك التسجيل بحساب جديد مباشرة)
    cursor.execute('''
        INSERT OR IGNORE INTO users (identifier, password) VALUES (?, ?)
    ''', ("admin@trading.com", "123456"))

    # قائمة الأسهم الأمريكية والمصرية والعملات الموسعة
    default_data = [
        ("NIO", "نيو للسيارات الكهربائية", "5.40", "45K", "15K", "عالية", "ارتداد من دعم قاع السنوي مع تدفق سيولة.", "نيو تعلن عن زيادة في تسليمات السيارات.", "US", "Assets"),
        ("SIRI", "سيريوس إكس إم", "3.20", "20K", "8K", "متوسطة", "استقرار عرضي وتجميع عند الدعم.", "أخبار حول إعادة هيكلة الأسهم.", "US", "Assets"),
        ("F", "فورد موتورز", "11.80", "60K", "25K", "عالية", "تماسك أعلى المتوسطات المتحركة.", "فورد توسع استثمارات البطاريات.", "US", "Assets"),
        ("PFE", "فايزر للأدوية", "27.50", "90K", "30K", "عالية جداً", "ضغط شراء استثماري طويل الأجل.", "عقود جديدة توافق عليها هيئة الدواء.", "US", "Assets"),
        ("INTC", "إنتل كورب", "21.30", "110K", "50K", "عالية جداً", "محاولات اختراق خط الاتجاه الهابط.", "إنتل تتلقى دعماً حكومياً جديداً.", "US", "Assets"),
        ("SOFI", "سوفي تكنولوجيز", "7.60", "75K", "20K", "عالية", "نشاط تداولات قوية ونمو في محفظة القروض.", "نتائج أعمال فصلية تفوق التوقعات.", "US", "Assets"),
        ("PLTR", "بالانتير تكنولوجيز", "24.10", "150K", "40K", "عالية جداً", "زخم صاعد قوي بطلب مؤسسي مكثف.", "عقود دفاعية جديدة للشركات.", "US", "Assets"),
        ("SNAP", "سناب شات", "10.50", "40K", "18K", "متوسطة", "تذبذب قرب مستويات المقاومة الفنية.", "تحديثات جديدة لتطبيق الإعلانات.", "US", "Assets"),
        ("AMD", "إيه إم دي", "155.00", "200K", "70K", "عالية جداً", "منافسة قوية واختراق مستويات العرض.", "إطلاق معالجات ذكاء اصطناعي جديدة.", "US", "Assets"),
        ("NVDA", "إنيديا", "130.20", "250K", "80K", "عالية جداً", "اختراق قمة الجلسة وطلب مؤسسي قوي.", "إنيديا تعلن عن رقائق جديدة بمعمارية متطورة.", "US", "Auto Scanner"),
        ("AAPL", "آبل", "185.50", "180K", "60K", "عالية جداً", "ثبات أعلى الدعم مع ضغط شرایی مؤسسي.", "آبل تسجل إيرادات فصلية قياسية.", "US", "Assets"),
        ("DICE", "دايس للصناعات", "2.05", "15K", "5K", "متوسطة", "نشاط ملحوظ بالسوق المصري وعروض شراء عند مستويات الدعم.", "تداولات نشطة على سهم دايس وسط ترقب لنتائج الأعمال.", "EG", "Assets"),
        ("COMI", "البنك التجاري الدولي", "80.00", "120K", "40K", "عالية جداً", "اتجاه صاعد واستقرار للسيولة المؤسسية.", "البنك يعلن عن توزيعات نقدية مرتقبة.", "EG", "Assets"),
        ("HELI", "مصر للصناعات الهندسية / هليوبوليس", "12.50", "35K", "12K", "متوسطة", "تحركات إيجابية قرب مستويات الدعم.", "تطوير أراضي جديدة للمشاريع.", "EG", "Assets"),
        ("PHDC", "بالم هيلز للتعمير", "5.80", "50K", "15K", "عالية", "حجم تداول مرتفع واختراق مقاومة فرعية.", "مبيعات عقارية قياسية بنهاية الربع.", "EG", "Assets"),
        ("EURUSD", "اليورو دولار", "1.0850", "100K", "90K", "عالية", "تذبذب عرضي حول مستويات الدعم مع سيولة متوازنة.", "الأسواق تترقب بيانات التضخم الأمريكية.", "Forex", "Assets"),
        ("GBPUSD", "السترليني دولار", "1.2650", "80K", "70K", "عالية", "ثبات أعلى مستويات الدعم الرئيسية للفنيات.", "تطورات اقتصادية هامة تؤثر على زوج الاسترليني.", "Forex", "Assets"),
        ("USDJPY", "الدولار ين", "155.20", "110K", "95K", "عالية جداً", "ترقب لتدخلات البنك المركزي عند مستويات المقاومة.", "بيانات بنك اليابان تقود التداولات.", "Forex", "Assets")
    ]
    
    for item in default_data:
        cursor.execute('''
            INSERT OR IGNORE INTO assets (symbol, name, price, demand, supply, liquidity, analysis, news, market, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', item)
    conn.commit()
    conn.close()

init_db()

AUTH_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول / إنشاء حساب - منصة التداول</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; direction: rtl; }
        .auth-card { background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); width: 100%; max-width: 400px; border: 1px solid #334155; text-align: center; }
        h2 { color: #38bdf8; margin-bottom: 15px; }
        input { width: 100%; padding: 12px; margin-bottom: 15px; background: #0f172a; color: #fff; border: 1px solid #334155; border-radius: 8px; box-sizing: border-box; outline: none; font-size: 15px; }
        button { width: 100%; background: #0284c7; color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; transition: 0.3s; margin-top: 5px; }
        button:hover { background: #0369a1; }
        .msg { font-size: 13px; margin-bottom: 15px; }
        .error { color: #ef4444; }
        .success { color: #22c55e; }
        .toggle-link { margin-top: 15px; display: block; color: #38bdf8; cursor: pointer; font-size: 14px; text-decoration: underline; }
    </style>
</head>
<body>
    <div class="auth-card">
        <h2 id="formTitle">تسجيل الدخول للمنصة</h2>
        {% if error %}
            <p class="msg error">{{ error }}</p>
        {% endif %}
        {% if success %}
            <p class="msg success">{{ success }}</p>
        {% endif %}
        <form id="authForm" method="POST" action="/login">
            <input type="text" name="identifier" placeholder="البريد الإلكتروني أو رقم الهاتف..." required>
            <input type="password" name="password" placeholder="كلمة المرور..." required>
            <button type="submit" id="submitBtn">دخول</button>
        </form>
        <span class="toggle-link" onclick="toggleMode()">ليس لديك حساب؟ اضغط هنا لإنشاء حساب جديد</span>
    </div>

    <script>
        let isLogin = true;
        function toggleMode() {
            const form = document.getElementById('authForm');
            const title = document.getElementById('formTitle');
            const btn = document.getElementById('submitBtn');
            const toggle = document.querySelector('.toggle-link');

            if (isLogin) {
                form.action = '/register';
                title.innerText = 'إنشاء حساب جديد';
                btn.innerText = 'تسجيل حساب';
                toggle.innerText = 'لديك حساب بالفعل؟ سجل دخولك من هنا';
                isLogin = false;
            } else {
                form.action = '/login';
                title.innerText = 'تسجيل الدخول للمنصة';
                btn.innerText = 'دخول';
                toggle.innerText = 'ليس لديك حساب؟ اضغط هنا لإنشاء حساب جديد';
                isLogin = true;
            }
        }
    </script>
</body>
</html>
"""

INDEX_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة التداول المتكاملة</title>
    <link rel="manifest" href="/manifest.json">
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; direction: rtl; }
        .container { max-width: 1100px; margin: auto; background: #1e293b; padding: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        .header-flex { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }
        h1 { color: #38bdf8; font-size: 22px; margin: 0; }
        .logout-btn { background: #ef4444; color: white; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: bold; }
        p.subtitle { color: #94a3b8; font-size: 13px; margin: 5px 0 15px 0; }
        
        .search-box { margin: 15px 0; text-align: center; }
        .search-box input { width: 100%; max-width: 500px; padding: 12px; font-size: 15px; background: #0f172a; color: #fff; border: 1px solid #334155; border-radius: 8px; outline: none; }

        .nav-tabs { display: flex; gap: 10px; margin-bottom: 20px; justify-content: center; flex-wrap: wrap; }
        .tab-btn { background: #334155; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: bold; transition: 0.3s; }
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
    <div class="header-flex">
        <div>
            <h1>منصة التداول المتكاملة</h1>
            <p class="subtitle">السكنر اللحظي، الأسهم الأمريكية والمصرية، والعملات مع بحث فوري شامل</p>
        </div>
        <a href="/logout"><button class="logout-btn">تسجيل الخروج</button></a>
    </div>
    
    <div class="search-box">
        <input type="text" id="globalSearch" placeholder="ابحث برمز السهم أو الاسم (مثال: NIO, دايس, EURUSD)..." oninput="filterData()">
    </div>

    <div class="nav-tabs">
        <button class="tab-btn active" onclick="switchTab('scanner', this)">📡 السكنر اللحظي</button>
        <button class="tab-btn" onclick="switchTab('us-stocks', this)">🇺🇸 الأسهم (أمريكية ومصرية)</button>
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
        <h3 style="color: #38bdf8;">قائمة الأسهم المتاحة والمعتمدة</h3>
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
    let globalAssets = [];

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
            globalAssets = data.assets;
            renderAll(globalAssets);
        } catch (error) {
            console.error('خطأ في جلب البيانات:', error);
        }
    }

    function renderAll(data) {
        const scannerTbody = document.getElementById('scannerTableBody');
        const stocksDiv = document.getElementById('stocksList');
        const forexDiv = document.getElementById('forexList');

        scannerTbody.innerHTML = '';
        stocksDiv.innerHTML = '<h4 style="color: #22c55e; margin-top:0;">الأسهم المتاحة:</h4>';
        forexDiv.innerHTML = '<h4 style="color: #22c55e; margin-top:0;">أزواج العملات:</h4>';

        let hasScanner = false;
        let hasStocks = false;
        let hasForex = false;

        if(!data || data.length === 0) {
            scannerTbody.innerHTML = '<tr><td colspan="8">لا توجد بيانات...</td></tr>';
            stocksDiv.innerHTML += '<p style="color: #94a3b8;">لا توجد نتائج...</p>';
            forexDiv.innerHTML += '<p style="color: #94a3b8;">لا توجد نتائج...</p>';
            return;
        }

        data.forEach((item) => {
            if (item.market !== 'Forex') {
                scannerTbody.innerHTML += `<tr onclick='openModal(${JSON.stringify(item)})'>
                    <td><span class="badge">${item.source || 'Scanner'}</span></td>
                    <td><b>${item.symbol}</b></td>
                    <td>${item.name}</td>
                    <td>${item.price}</td>
                    <td style="color: #22c55e;">${item.demand || '0'}</td>
                    <td style="color: #ef4444;">${item.supply || '0'}</td>
                    <td><b>${item.liquidity || 'عادية'}</b></td>
                    <td>${item.analysis || ''}</td>
                </tr>`;
                hasScanner = true;
            }

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

        if (!hasScanner) scannerTbody.innerHTML = '<tr><td colspan="8">لا توجد إشارات في السكنر.</td></tr>';
        if (!hasStocks) stocksDiv.innerHTML += '<p style="color: #94a3b8;">لا توجد أسهم مطابقة.</p>';
        if (!hasForex) forexDiv.innerHTML += '<p style="color: #94a3b8;">لا توجد عملات مطابقة.</p>';
    }

    function filterData() {
        const query = document.getElementById('globalSearch').value.toLowerCase().trim();
        if (!query) {
            renderAll(globalAssets);
            return;
        }
        const filtered = globalAssets.filter(item => 
            (item.symbol && item.symbol.toLowerCase().includes(query)) || 
            (item.name && item.name.toLowerCase().includes(query)) ||
            (item.market && item.market.toLowerCase().includes(query)) ||
            (item.source && item.source.toLowerCase().includes(query))
        );
        renderAll(filtered);
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

    setInterval(fetchAppData, 5000);
    fetchAppData();
</script>

</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE identifier = ? AND password = ?", (identifier, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['logged_in'] = True
            session['user'] = identifier
            return redirect(url_for('home'))
        else:
            error = "بيانات الدخول غير صحيحة. تأكد من البريد/الهاتف وكلمة المرور."
    return render_template_string(AUTH_HTML, error=error)

@app.route('/register', methods=['POST'])
def register():
    identifier = request.form.get('identifier')
    password = request.form.get('password')
    
    if not identifier or not password:
        return render_template_string(AUTH_HTML, error="يرجى إدخال البريد/الهاتف وكلمة المرور.")
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (identifier, password) VALUES (?, ?)", (identifier, password))
        conn.commit()
        conn.close()
        return render_template_string(AUTH_HTML, success="تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.")
    except sqlite3.IntegrityError:
        return render_template_string(AUTH_HTML, error="هذا البريد أو رقم الهاتِف مستخدم مسبقاً.")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template_string(INDEX_HTML)

@app.route('/manifest.json')
def manifest():
    manifest_data = {
        "name": "منصة التداول المتكاملة",
        "short_name": "منصة التداول",
        "description": "منصة متكاملة للسكنر اللحظي والأسهم والعملات",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0f172a",
        "theme_color": "#0284c7",
        "icons": [
            {
                "src": "https://img.icons8.com/color/512/stocks.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    return jsonify(manifest_data)

@app.route('/api/app-data', methods=['GET'])
def get_app_data():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets")
    rows = cursor.fetchall()
    conn.close()
    
    assets_list = [dict(row) for row in rows]
    return jsonify({"assets": assets_list})

@app.route('/api/webhook-update', methods=['POST'])
def webhook_update():
    incoming_data = request.json
    if incoming_data:
        symbol = incoming_data.get("symbol", "N/A")
        name = incoming_data.get("name", "غير محدد")
        price = incoming_data.get("price", "0.00")
        demand = incoming_data.get("demand", "0")
        supply = incoming_data.get("supply", "0")
        liquidity = incoming_data.get("liquidity", "عادية")
        analysis = incoming_data.get("analysis", "تحديث آلي مباشر")
        news = incoming_data.get("news", "أخبار فورية مرصودة.")
        market = incoming_data.get("market", "US")
        source = incoming_data.get("source", "Auto Scanner")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO assets (symbol, name, price, demand, supply, liquidity, analysis, news, market, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, name, price, demand, supply, liquidity, analysis, news, market, source))
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
