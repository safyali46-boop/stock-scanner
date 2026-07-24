from flask import Flask, jsonify, request, render_template_string, session, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ultimate_trading_scanner_secret_key"
DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # جدول الأصول الموحد لكل الأسواق والسكنر
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
    
    # جدول المستخدمين للدخول أو التسجيل
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier TEXT UNIQUE,
            password TEXT
        )
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO users (identifier, password) VALUES (?, ?)
    ''', ("admin@trading.com", "123456"))

    # عينة من الأسهم الأمريكية (تحت 50 دولار) ومصرية وعملات ومعادن كمخزون ابتدائي
    default_data = [
        # الأسهم الأمريكية (حتى 50 دولار) مع تفاصيل التحليل الفني
        ("NIO", "نيو للسيارات", "5.40", "45K", "15K", "عالية", "موجي: قاع صاعد | موفينج: تقاطع إيجابي | ماكد: صاعد | رقمي: دعم قوي | فيبو: تصحيح 61.8%", "زيادة تسليمات السيارات الكهربائية.", "US_STOCKS", "Assets"),
        ("F", "فورد موتورز", "11.80", "60K", "25K", "عالية", "موجي: موجة 3 دافعة | موفينج: فوق 50 | ماكد: إيجابي | رقمي: ثبات فوق 11 | فيبو: ارتداد من 38.2%", "توسعات جديدة في قطاع البطاريات.", "US_STOCKS", "Assets"),
        ("SOFI", "سوفي تكنولوجيز", "7.60", "75K", "20K", "عالية", "موجي: نهاية تصحيح | موفينج: تقاطع ذهبي | ماكد: تقاطع إيجابي | رقمي: مقاومة مختترقة | فيبو: هدف 50%", "نتائج أعمال فصلية ممتازة.", "US_STOCKS", "Assets"),
        ("PLTR", "بالانتير", "24.10", "150K", "40K", "عالية جداً", "موجي: اندفاع قوي | موفينج: ترند صاعد | ماكد: زخم عالي | رقمي: صدارة السيولة | فيبو: امتداد 1.618", "عقود دفاعية جديدة ضخمة.", "US_STOCKS", "Assets"),
        ("INTC", "إنتل", "21.30", "110K", "50K", "عالية جداً", "موجي: قاع تاريخي | موفينج: قرب المتوسط | ماكد: ارتداد | رقمي: دعم 20 | فيبو: دعم رئيسي", "دعم حكومي لقطاع الرقائق.", "US_STOCKS", "Assets"),
        
        # الأسهم المصرية (EGX)
        ("DICE", "دايس للصناعات", "2.05", "15K", "5K", "متوسطة", "موجي: تجميع صاعد | موفينج: استقرار | ماكد: محايد | رقمي: دعم 2.00 | فيبو: ارتداد 50%", "نشاط تداولات ترقب لنتائج الأعمال.", "EGX", "Assets"),
        ("COMI", "البنك التجاري الدولي", "80.00", "120K", "40K", "عالية جداً", "موجي: موجة رئيسية صاعدة | موفينج: ترتيب إيجابي | ماكد: صاعد | رقمي: قمة جديدة | فيبو: استقرار", "توزيعات نقدية مرتقبة.", "EGX", "Assets"),
        ("PHDC", "بالم هيلز", "5.80", "50K", "15K", "عالية", "موجي: اختراق قناة | موفينج: فوق المتوسطات | ماكد: إيجابي | رقمي: مقاومة 5.70 | فيبو: هدف 6.20", "مبيعات عقارية قياسية.", "EGX", "Assets"),

        # العملات والفوركس
        ("EURUSD", "اليورو دولار", "1.0850", "100K", "90K", "عالية", "موجي: عرضي متماسك | موفينج: تداخل | ماكد: هادئ | رقمي: دعم 1.08 | فيبو: 50% ريتارسمينت", "ترقب بيانات التضخم الأمريكية.", "FOREX", "Assets"),
        ("GBPUSD", "السترليني دولار", "1.2650", "80K", "70K", "عالية", "موجي: صاعد تدريجي | موفينج: إيجابي | ماكد: صاعد | رقمي: دعم 1.26 | فيبو: هدف 1.275", "بيانات اقتصادية بريطانية قوية.", "FOREX", "Assets"),

        # المعادن (الذهب والفضة)
        ("XAUUSD", "الذهب (Gold)", "2380.00", "500K", "200K", "عالية جداً", "موجي: موجة 5 صاعدة | موفينج: دعم قوي | ماكد: زخم إيجابي | رقمي: دعم 2350 | فيبو: امتداد تاريخي", "توترات جيوستراتيجية تدعم الملاذ الآمن.", "METALS", "Assets")
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
    <title>تسجيل الدخول - منصة السكنر الشاملة</title>
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
    <title>منصة السكنر الشاملة (الأسواق العالمية والمحلية)</title>
    <link rel="manifest" href="/manifest.json">
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; direction: rtl; }
        .container { max-width: 1200px; margin: auto; background: #1e293b; padding: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        .header-flex { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }
        h1 { color: #38bdf8; font-size: 22px; margin: 0; }
        .logout-btn { background: #ef4444; color: white; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: bold; }
        p.subtitle { color: #94a3b8; font-size: 13px; margin: 5px 0 15px 0; }
        
        .search-box { margin: 15px 0; text-align: center; }
        .search-box input { width: 100%; max-width: 500px; padding: 12px; font-size: 15px; background: #0f172a; color: #fff; border: 1px solid #334155; border-radius: 8px; outline: none; }

        .nav-tabs { display: flex; gap: 8px; margin-bottom: 20px; justify-content: center; flex-wrap: wrap; }
        .tab-btn { background: #334155; color: white; border: none; padding: 9px 15px; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: bold; transition: 0.3s; }
        .tab-btn.active, .tab-btn:hover { background: #0284c7; }

        .section-content { display: none; }
        .section-content.active { display: block; }

        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 10px; border: 1px solid #334155; text-align: center; font-size: 12px; cursor: pointer; }
        th { background-color: #0f172a; color: #38bdf8; cursor: default; }
        tr:hover { background-color: #334155; }
        .badge { background: #0284c7; color: white; padding: 3px 6px; border-radius: 4px; font-size: 11px; }
        
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.7); justify-content: center; align-items: center; }
        .modal-content { background-color: #1e293b; padding: 25px; border-radius: 10px; width: 550px; max-width: 90%; border: 1px solid #334155; text-align: right; max-height: 85vh; overflow-y: auto; }
        .close-btn { background: #ef4444; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; float: left; font-weight: bold; }
        .card { background: #0f172a; padding: 12px; border-radius: 8px; border: 1px solid #334155; margin-top: 10px; cursor: pointer; transition: 0.2s; }
        .card:hover { border-color: #38bdf8; }
    </style>
</head>
<body>

<div class="container">
    <div class="header-flex">
        <div>
            <h1>منصة السكنر الشاملة</h1>
            <p class="subtitle">السكنر الخارجي اللحظي، الأسهم الأمريكية (حتى 50$)، المصرية، العملات، والمعادن</p>
        </div>
        <a href="/logout"><button class="logout-btn">تسجيل الخروج</button></a>
    </div>
    
    <div class="search-box">
        <input type="text" id="globalSearch" placeholder="ابحث برمز السهم أو الاسم في كل الأسواق (مثال: NIO, دايس, EURUSD, XAUUSD)..." oninput="filterData()">
    </div>

    <div class="nav-tabs">
        <button class="tab-btn active" onclick="switchTab('scanner', this)">📡 سكنر الإشارات الخارجية</button>
        <button class="tab-btn" onclick="switchTab('us-stocks', this)">🇺🇸 الأسهم الأمريكية (&lt;50$)</button>
        <button class="tab-btn" onclick="switchTab('egypt-stocks', this)">🇪🇬 البورصة المصرية</button>
        <button class="tab-btn" onclick="switchTab('forex', this)">💱 العملات (Forex)</button>
        <button class="tab-btn" onclick="switchTab('metals', this)">🪙 المعادن والسلع</button>
    </div>

    <!-- تبيوب السكنر الخارجي -->
    <div id="scanner" class="section-content active">
        <h3 style="color: #38bdf8;">إشارات السكنر الخارجي (تحديث آلي لآخر اليوم)</h3>
        <table>
            <thead>
                <tr>
                    <th>المصدر</th>
                    <th>الرمز</th>
                    <th>الاسم</th>
                    <th>السعر</th>
                    <th>الطلب</th>
                    <th>العرض</th>
                    <th>السيولة</th>
                    <th>التحليل الشامل</th>
                </tr>
            </thead>
            <tbody id="scannerTableBody"></tbody>
        </table>
    </div>

    <!-- تبويب الأسهم الأمريكية -->
    <div id="us-stocks" class="section-content">
        <h3 style="color: #38bdf8;">الأسهم الأمريكية (حتى 50 دولار)</h3>
        <div id="usList"></div>
    </div>

    <!-- تبويب البورصة المصرية -->
    <div id="egypt-stocks" class="section-content">
        <h3 style="color: #38bdf8;">الأسهم والبورصة المصرية (EGX)</h3>
        <div id="egyptList"></div>
    </div>

    <!-- تبويب العملات -->
    <div id="forex" class="section-content">
        <h3 style="color: #38bdf8;">أزواج العملات (Forex)</h3>
        <div id="forexList"></div>
    </div>

    <!-- تبويب المعادن -->
    <div id="metals" class="section-content">
        <h3 style="color: #38bdf8;">المعادن والسلع (Metals)</h3>
        <div id="metalsList"></div>
    </div>

</div>

<!-- نافذة التفاصيل الشاملة (التحليل الموجي، موفينج، ماكد، رقمي، فيبو، الأخبار) -->
<div id="stockModal" class="modal">
    <div class="modal-content">
        <button class="close-btn" onclick="closeModal()">إغلاق</button>
        <h2 id="modalSymbol" style="color: #38bdf8; margin-top: 0;"></h2>
        <p><b>الاسم:</b> <span id="modalName"></span> | <b>السعر:</b> <span id="modalPrice"></span></p>
        <hr style="border-color: #334155;">
        <h3 style="color: #22c55e; font-size: 15px;">حجم الطلب والعرض والسيولة:</h3>
        <p id="modalSupplyDemand" style="color: #f8fafc; font-size: 13px;"></p>
        <h3 style="color: #38bdf8; font-size: 15px;">التحليل الفني المتقدم (موجي، موفينج، ماكد، رقمي، فيبو):</h3>
        <p id="modalAnalysis" style="color: #f8fafc; font-size: 13px; line-height: 1.6; background: #0f172a; padding: 10px; border-radius: 6px;"></p>
        <h3 style="color: #eab308; font-size: 15px;">الأخبار العاجلة والأسباب:</h3>
        <p id="modalNews" style="color: #94a3b8; font-size: 13px; line-height: 1.5;"></p>
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
        const usDiv = document.getElementById('usList');
        const egyptDiv = document.getElementById('egyptList');
        const forexDiv = document.getElementById('forexList');
        const metalsDiv = document.getElementById('metalsList');

        scannerTbody.innerHTML = '';
        usDiv.innerHTML = '<h4 style="color: #22c55e; margin-top:0;">الأسهم الأمريكية المتاحة:</h4>';
        egyptDiv.innerHTML = '<h4 style="color: #22c55e; margin-top:0;">الأسهم المصرية المتاحة:</h4>';
        forexDiv.innerHTML = '<h4 style="color: #22c55e; margin-top:0;">أزواج العملات:</h4>';
        metalsDiv.innerHTML = '<h4 style="color: #22c55e; margin-top:0;">المعادن والسلع:</h4>';

        let hasScanner = false;
        let hasUS = false;
        let hasEgypt = false;
        let hasForex = false;
        let hasMetals = false;

        if(!data || data.length === 0) {
            scannerTbody.innerHTML = '<tr><td colspan="8">لا توجد إشارات سكنر حالياً...</td></tr>';
            return;
        }

        data.forEach((item) => {
            // كل إشارة واردة من السكنر الخارجي أو مسجلة تظهر في جدول السكنر الموحد
            scannerTbody.innerHTML += `<tr onclick='openModal(${JSON.stringify(item)})'>
                <td><span class="badge">${item.source || 'Scanner'}</span></td>
                <td><b>${item.symbol}</b></td>
                <td>${item.name}</td>
                <td>${item.price}</td>
                <td style="color: #22c55e;">${item.demand || '0'}</td>
                <td style="color: #ef4444;">${item.supply || '0'}</td>
                <td><b>${item.liquidity || 'عادية'}</b></td>
                <td>${item.analysis ? item.analysis.substring(0, 45) + '...' : ''}</td>
            </tr>`;
            hasScanner = true;

            const cardHTML = `<div class="card" onclick='openModal(${JSON.stringify(item)})'>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <b style="color: #38bdf8; font-size: 15px;">${item.symbol} - ${item.name}</b>
                    <span class="badge">السعر: ${item.price}</span>
                </div>
                <p style="color: #94a3b8; font-size: 12px; margin: 6px 0 0 0;"><b>التحليل الشامل:</b> ${item.analysis}</p>
            </div>`;

            if (item.market === 'US_STOCKS') {
                usDiv.innerHTML += cardHTML;
                hasUS = true;
            } else if (item.market === 'EGX') {
                egyptDiv.innerHTML += cardHTML;
                hasEgypt = true;
            } else if (item.market === 'FOREX') {
                forexDiv.innerHTML += cardHTML;
                hasForex = true;
            } else if (item.market === 'METALS') {
                metalsDiv.innerHTML += cardHTML;
                hasMetals = true;
            } else {
                // إذا جاء سهم عام من السكنر الخارجي يضاف افتراضياً للأمريكي أو العام
                usDiv.innerHTML += cardHTML;
                hasUS = true;
            }
        });

        if (!hasScanner) scannerTbody.innerHTML = '<tr><td colspan="8">لا توجد إشارات واردة حتى الآن.</td></tr>';
        if (!hasUS) usDiv.innerHTML += '<p style="color: #94a3b8;">لا توجد أسهم مطابقة.</p>';
        if (!hasEgypt) egyptDiv.innerHTML += '<p style="color: #94a3b8;">لا توجد أسهم مطابقة.</p>';
        if (!hasForex) forexDiv.innerHTML += '<p style="color: #94a3b8;">لا توجد عملات مطابقة.</p>';
        if (!hasMetals) metalsDiv.innerHTML += '<p style="color: #94a3b8;">لا توجد معادن مطابقة.</p>';
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
        document.getElementById('modalSupplyDemand').innerHTML = `الطلب: <span style="color: #22c55e;">${item.demand || 'N/A'}</span> | العرض: <span style="color: #ef4444;">${item.supply || 'N/A'}</span> | السيولة: <b>${item.liquidity || 'عادية'}</b>`;
        document.getElementById('modalAnalysis').innerText = item.analysis || "تحت الفحص الفني الشامل.";
        document.getElementById('modalNews').innerText = item.news || "لا توجد أخبار مسجلة حالياً لهذا الأصل.";
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
        "name": "منصة السكنر الشاملة",
        "short_name": "السكنر الشامل",
        "description": "منصة متكاملة للسكنر الخارجي وأسواق المال",
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
        liquidity = incoming_data.get("liquidity", "عالية")
        analysis = incoming_data.get("analysis", "موجي: إيجابي | موفينج: مرتب | ماكد: صاعد | رقمي: دعم | فيبو: هدف مرتفع")
        news = incoming_data.get("news", "أخبار مرصدة من السكنر الخارجي.")
        market = incoming_data.get("market", "US_STOCKS")
        source = incoming_data.get("source", "External Scanner")

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
