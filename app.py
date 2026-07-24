from flask import Flask, jsonify, request, render_template_string
import os

app = Flask(__name__)

# صفحة الواجهة الرئيسية
INDEX_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>السكنر السحابي للأسهم</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; direction: rtl; }
        .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #2c3e50; }
        .filters { display: flex; gap: 10px; margin-bottom: 20px; }
        input, select { padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 5px; flex: 1; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; border: 1px solid #ddd; text-align: center; }
        th { background-color: #2c3e50; color: white; }
        .positive { color: green; font-weight: bold; }
    </style>
</head>
<body>

<div class="container">
    <h1>السكنر السحابي للأسهم</h1>
    
    <div class="filters">
        <select id="marketSelect" onchange="loadData()">
            <option value="الامريكية">السوق الأمريكية</option>
            <option value="المصرية">السوق المصرية</option>
        </select>
        <input type="text" id="searchInput" placeholder="ابحث برمز أو اسم السهم..." onkeyup="loadData()">
    </div>

    <table>
        <thead>
            <tr>
                <th>الرمز</th>
                <th>اسم السهم</th>
                <th>السعر</th>
                <th>التغير</th>
                <th>التحليل الفني</th>
            </tr>
        </thead>
        <tbody id="tableBody">
            <!-- سيتم تحميل البيانات هنا تلقائياً -->
        </tbody>
    </table>
</div>

<script>
    async function loadData() {
        const market = document.getElementById('marketSelect').value;
        const query = document.getElementById('searchInput').value;
        
        try {
            const response = await fetch(`/api/market?market=${market}&q=${query}`);
            const data = await response.json();
            
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';
            
            if(data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5">لا توجد نتائج مطابقة</td></tr>';
                return;
            }

            data.forEach(item => {
                const row = `<tr>
                    <td><b>${item.symbol}</b></td>
                    <td>${item.name}</td>
                    <td>${item.price}</td>
                    <td class="positive">+${item.change}%</td>
                    <td>${item.analysis}</td>
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
    market = request.args.get('market', 'المصرية')
    query = request.args.get('q', '').lower()
    
    # بيانات تجريبية (أو بيانات السكنر بتاعتك)
    mock_data = [
        {"symbol": "AAPL", "name": "أبل", "price": "180.5", "change": "2.4", "analysis": "إيجابي قوي"},
        {"symbol": "TSLA", "name": "تسلا", "price": "210.0", "change": "1.8", "analysis": "حيادي"},
        {"symbol": "DICE", "name": "دايس للصناعات", "price": "2.05", "change": "3.1", "analysis": "فرصة شراء"}
    ]
    
    # فلترة بناءً على البحث
    filtered = [
        item for item in mock_data 
        if query in item['symbol'].lower() or query in item['name'].lower()
    ]
    
    return jsonify(filtered)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
