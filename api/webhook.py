from flask import Flask, request, jsonify
import os
import sys
import logging

# إضافة المسار الرئيسي للمشروع
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.facebook import FacebookAPI
from utils.replies import ReplyManager

# إنشاء تطبيق Flask
app = Flask(__name__)

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# تهيئة الكلاسات (مع التحقق من المتغيرات)
try:
    fb_api = FacebookAPI()
    reply_manager = ReplyManager()
    logger.info("✅ تم تهيئة البوت بنجاح")
except Exception as e:
    logger.error(f"❌ فشل تهيئة البوت: {str(e)}")
    fb_api = None
    reply_manager = None

@app.route('/', methods=['GET', 'POST'])
@app.route('/api/webhook', methods=['GET', 'POST'])
def webhook():
    """
    نقطة النهاية الرئيسية للـ Webhook
    GET: للتحقق من صحة الـ Webhook (يتم مرة واحدة عند الإعداد)
    POST: لاستقبال الأحداث من فيسبوك
    """
    
    # ========== معالجة طلبات GET (التحقق من Webhook) ==========
    if request.method == 'GET':
        # قراءة المعاملات من الرابط
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        # قراءة رمز التحقق من المتغيرات البيئية
        verify_token = os.getenv('VERIFICATION_TOKEN', '')
        
        logger.info("=" * 50)
        logger.info("🔍 طلب تحقق Webhook مستلم!")
        logger.info(f"📌 mode: {mode}")
        logger.info(f"📌 token المستلم: {token}")
        logger.info(f"📌 token المتوقع: {verify_token}")
        logger.info(f"📌 challenge: {challenge}")
        logger.info("=" * 50)
        
        # التحقق من الرمز
        if mode == 'subscribe' and token == verify_token and verify_token != '':
            logger.info("✅✅✅ التحقق ناجح! ✅✅✅")
            return challenge, 200
        else:
            logger.warning("❌❌❌ فشل التحقق ❌❌❌")
            if verify_token == '':
                logger.error("⚠️ VERIFICATION_TOKEN غير مضبوط في المتغيرات البيئية!")
            return "Verification failed", 403
    
    # ========== معالجة طلبات POST (الأحداث الواردة) ==========
    elif request.method == 'POST':
        logger.info("=" * 50)
        logger.info("📩 استقبال حدث POST من فيسبوك")
        
        # التأكد من أن الفيسبوك API مهيأ
        if not fb_api or not reply_manager:
            logger.error("❌ البوت لم يتم تهيئته بشكل صحيح")
            return jsonify({"status": "error", "message": "Bot not initialized"}), 500
        
        try:
            # استلام البيانات
            data = request.get_json()
            logger.info(f"📦 البيانات المستلمة: {data}")
            
            # تحليل البيانات واستخراج التعليقات الجديدة
            comments = fb_api.parse_webhook_data(data)
            logger.info(f"📝 عدد التعليقات المستخرجة: {len(comments)}")
            
            # معالجة كل تعليق
            for i, comment in enumerate(comments):
                logger.info(f"🔄 معالجة تعليق #{i+1}: {comment.get('comment_id')}")
                
                try:
                    # التحقق مما إذا كان يجب الرد
                    if reply_manager.should_reply(comment):
                        # توليد الرد
                        reply_text = reply_manager.generate_reply(comment)
                        
                        # الرد على التعليق
                        if comment.get('comment_id'):
                            fb_api.reply_to_comment(comment['comment_id'], reply_text)
                            logger.info(f"✅ تم الرد على التعليق: {comment['comment_id']}")
                    else:
                        logger.info(f"⏭️ تخطي الرد على التعليق: {comment.get('comment_id')}")
                        
                except Exception as e:
                    logger.error(f"❌ خطأ في معالجة تعليق: {str(e)}")
                    continue
            
            logger.info("✅✅✅ تمت معالجة جميع التعليقات بنجاح ✅✅✅")
            return jsonify({"status": "success"}), 200
            
        except Exception as e:
            logger.error(f"❌ خطأ عام في معالجة الطلب: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500

# للاختبار المحلي
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', debug=True, port=port)
