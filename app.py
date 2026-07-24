from flask import Flask, render_template, request, jsonify

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
    return render_template('scanner.html', stocks=scanner_results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
