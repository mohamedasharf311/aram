import os
import requests
import logging
from typing import Dict, Any, Optional

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FacebookAPI:
    """التعامل مع Facebook Graph API"""
    
    BASE_URL = "https://graph.facebook.com/v18.0"
    
    def __init__(self):
        self.access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
        self.page_id = os.getenv("FACEBOOK_PAGE_ID")
        
        if not self.access_token or not self.page_id:
            raise ValueError("❌ يجب تعيين FACEBOOK_PAGE_ACCESS_TOKEN و FACEBOOK_PAGE_ID")
        
        logger.info("✅ تم تهيئة Facebook API بنجاح")
    
    def reply_to_comment(self, comment_id: str, message: str) -> Dict[str, Any]:
        """
        الرد على تعليق معين
        
        Args:
            comment_id: معرف التعليق
            message: نص الرد
            
        Returns:
            استجابة API
        """
        url = f"{self.BASE_URL}/{comment_id}/comments"
        params = {
            "message": message,
            "access_token": self.access_token
        }
        
        try:
            logger.info(f"📤 جاري الرد على التعليق {comment_id}")
            response = requests.post(url, params=params)
            response.raise_for_status()
            logger.info(f"✅ تم الرد على التعليق {comment_id} بنجاح")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ فشل الرد على التعليق {comment_id}: {str(e)}")
            raise
    
    def parse_webhook_data(self, data: Dict[str, Any]) -> list:
        """
        تحليل بيانات Webhook الواردة واستخراج التعليقات الجديدة
        
        Returns:
            قائمة تحتوي على معلومات التعليقات الجديدة
        """
        comments_to_reply = []
        
        try:
            if 'entry' not in data:
                return comments_to_reply
            
            for entry in data['entry']:
                if 'changes' not in entry:
                    continue
                
                for change in entry['changes']:
                    if change.get('field') == 'comments':
                        value = change.get('value', {})
                        
                        comment_data = {
                            'comment_id': value.get('comment_id'),
                            'post_id': value.get('post_id'),
                            'message': value.get('message'),
                            'from': value.get('from', {}),
                            'created_time': value.get('created_time'),
                            'parent_id': value.get('parent_id'),
                            'is_reply': value.get('parent_id') is not None
                        }
                        
                        comments_to_reply.append(comment_data)
                        logger.info(f"📝 تعليق جديد: {comment_data}")
            
            return comments_to_reply
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحليل بيانات Webhook: {str(e)}")
            return comments_to_reply
