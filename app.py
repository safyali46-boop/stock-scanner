from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# قائمة مؤقتة لتخزين نتائج الاسكنر وعرضها في التطبيق
scanner_results = []

@app.route('/api/webhook-update', methods=['POST'])
def webhook_update():
    data = request.json
    if data:
        # إضافة البيانات الجديدة في أول القائمة
        scanner_results.insert(0, data)
        # الاحتفاظ بآخر 50 نتيجة فقط عشان الذاكرة
        if len(scanner_results) > 50:
            scanner_results.pop()
        return jsonify({"status": "success", "message": "تم استلام البيانات بنجاح"}), 200
    return jsonify({"status": "error", "message": "لا توجد بيانات"}), 400

@app.route('/scanner')
def scanner_view():
    # عرض النتائج في صفحة أو أيقونة الاسكنر
    return render_template('scanner.html', results=scanner_results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
