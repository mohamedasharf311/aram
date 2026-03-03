from flask import Flask, request, jsonify
import os
import sys
import logging

# إضافة المسار الرئيسي للمشروع
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.facebook import FacebookAPI
from utils.replies import ReplyManager

# إعداد Flask
app = Flask(__name__)

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# تهيئة الكلاسات
try:
    fb_api = FacebookAPI()
    reply_manager = ReplyManager()
    logger.info("✅ تم تهيئة البوت بنجاح")
except Exception as e:
    logger.error(f"❌ فشل تهيئة البوت: {str(e)}")
    fb_api = None
    reply_manager = None

@app.route('/', methods=['GET', 'POST'])
def webhook():
    """
    نقطة النهاية الرئيسية للـ Webhook
    GET: للتحقق من صحة الـ Webhook (يتم مرة واحدة عند الإعداد)
    POST: لاستقبال الأحداث من فيسبوك
    """
    
    # التحقق من GET (طلبات التحقق)
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if fb_api:
            result = fb_api.verify_webhook(mode, token, challenge)
            if result:
                return result, 200
        
        return "Verification failed", 403
    
    # معالجة POST (الأحداث الواردة)
    elif request.method == 'POST':
        # التأكد من أن الفيسبوك API مهيأ
        if not fb_api or not reply_manager:
            logger.error("❌ البوت لم يتم تهيئته بشكل صحيح")
            return jsonify({"status": "error", "message": "Bot not initialized"}), 500
        
        try:
            # استلام البيانات
            data = request.get_json()
            logger.info(f"📩 استقبال بيانات: {data}")
            
            # تحليل البيانات واستخراج التعليقات الجديدة
            comments = fb_api.parse_webhook_data(data)
            
            # معالجة كل تعليق
            for comment in comments:
                try:
                    # التحقق مما إذا كان يجب الرد على هذا التعليق
                    if reply_manager.should_reply(comment):
                        # توليد الرد المناسب
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
            
            return jsonify({"status": "success"}), 200
            
        except Exception as e:
            logger.error(f"❌ خطأ عام في معالجة الطلب: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500

# للاختبار المحلي
if __name__ == '__main__':
    app.run(debug=True, port=5000)
