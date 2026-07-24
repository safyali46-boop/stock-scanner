from flask import Flask, request, jsonify

app = Flask(__name__)

# قائمة مؤقتة لتخزين الأسهم
scanner_results = []

@app.route('/')
def home():
    return "<h1>مرحباً بك في نظام الاسكنر شغال 100%</h1><p>اضغط على <a href='/scanner'>رابط الاسكنر</a> لرؤية النتائج.</p>"

@app.route('/api/webhook-update', methods=['POST'])
def webhook_update():
    data = request.json
    if data:
        scanner_results.insert(0, data)
        if len(scanner_results) > 50:
            scanner_results.pop()
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/scanner')
def scanner_view():
    html = "<h2 style='text-align:center;'>📊 نتائج الاسكنر الحيّة</h2>"
    html += "<table border='1' style='margin:auto; width:80%; text-align:center; border-collapse:collapse; font-family:Tahoma;'>"
    html += "<tr style='background:#007bff; color:white;'><th>الرمز</th><th>اسم السهم</th><th>السعر</th><th>الإشارة</th><th>المصدر</th></tr>"
    
    if scanner_results:
        for item in scanner_results:
            html += f"<tr><td><b>{item.get('symbol')}</b></td><td>{item.get('name')}</td><td>{item.get('price')}</td><td style='color:green; font-weight:bold;'>{item.get('signal')}</td><td>{item.get('source')}</td></tr>"
    else:
        html += "<tr><td colspan='5' style='padding:20px; color:#777;'>لا توجد بيانات حالياً... انتظر التحديث القادم!</td></tr>"
    
    html += "</table>"
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
