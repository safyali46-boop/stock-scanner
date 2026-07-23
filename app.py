from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

market_database = [
    { 'symbol': 'COMI', 'name': 'البنك التجاري الدولي', 'price': 78.25, 'change': 3.1, 'market': 'المصرية', 'type': 'أسهم', 'analysis': 'شراء قوي - توافق مع فيبوناتشي', 'fib': 'الدعم: 76.5 | المقاومة: 80.0', 'sma': 'إيجابي' },
    { 'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 185.50, 'change': 2.4, 'market': 'الامريكية', 'type': 'أسهم', 'analysis': 'زخم شراء ممتاز - جاهز للمضاربة السريعة', 'fib': 'الدعم: 182.0 | المقاومة: 190.0', 'sma': 'إيجابي' }
]

@app.route('/')
def home():
    return "السكنر السحابي يعمل بنجاح!"

@app.route('/api/market')
def get_market():
    market = request.args.get('market', 'الامريكية')
    q = request.args.get('q', '').strip().lower()
    filtered = [i for i in market_database if i['market'] == market and (not q or q in i['symbol'].lower() or q in i['name'].lower())]
    return jsonify(filtered)

@app.route('/api/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data and 'symbol' in data:
        market_database.insert(0, data)
        return jsonify({"status": "success", "message": "تم إضافة السهم بنجاح"})
    return jsonify({"status": "error"}), 400

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)