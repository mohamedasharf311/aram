import os
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
@app.route('/api/webhook', methods=['GET', 'POST'])
def webhook():
    # معالجة طلبات GET (التحقق من Webhook)
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        # قراءة رمز التحقق من المتغيرات البيئية
        verify_token = os.environ.get('VERIFICATION_TOKEN', '')

        # للتأكد من القيم، يمكنك إضافة سطر طباعة (سيظهر في سجلات Vercel)
        print(f"🔍 Received token: {token}, Expected: {verify_token}")

        # التحقق
        if mode == 'subscribe' and token == verify_token and token != '':
            print("✅ Verification successful!")
            return challenge, 200
        else:
            print("❌ Verification failed")
            return "Verification failed", 403

    # معالجة طلبات POST (الأحداث الواردة)
    elif request.method == 'POST':
        # ... باقي الكود الخاص بمعالجة التعليقات ...
        return "OK", 200
