import os
import random
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ReplyManager:
    """إدارة الردود التلقائية"""
    
    def __init__(self):
        # الردود الافتراضية (يمكن تعديلها أو إضافتها)
        self.default_replies = [
            "شكراً لتعليقك! نحن نقدر وقتك.",
            "نقدر تفاعلك معنا! شكراً لك.",
            "تعليقك يعني لنا الكثير، شكراً!",
            "نحن سعداء بتواصلك معنا، شكراً جزيلاً.",
            "شكراً لمشاركتنا رأيك! نتمنى لك يوماً سعيداً."
        ]
        
        # يمكن أيضاً قراءة الرد من متغير البيئة
        env_reply = os.getenv("REPLY_MESSAGE")
        if env_reply:
            self.default_replies.insert(0, env_reply)
    
    def generate_reply(self, comment_data: Dict[str, Any]) -> str:
        """
        توليد رد مناسب للتعليق
        
        Args:
            comment_data: بيانات التعليق
            
        Returns:
            نص الرد
        """
        comment_text = comment_data.get('message', '').lower()
        commenter_name = comment_data.get('from', {}).get('name', '')
        
        # يمكنك إضافة منطق أكثر ذكاءً هنا
        # مثلاً: ردود مختلفة حسب محتوى التعليق
        
        # اختيار رد عشوائي من القائمة
        reply = random.choice(self.default_replies)
        
        # إضافة اسم المعلق إذا أردت
        if commenter_name and random.choice([True, False]):  # 50% احتمال
            reply = f"{commenter_name}، {reply}"
        
        logger.info(f"💬 تم توليد رد: {reply}")
        return reply
    
    def should_reply(self, comment_data: Dict[str, Any]) -> bool:
        """
        تحديد ما إذا كان يجب الرد على هذا التعليق
        
        Args:
            comment_data: بيانات التعليق
            
        Returns:
            True إذا كان يجب الرد
        """
        # عدم الرد إذا كان التعليق نفسه رداً (لتجنب الرد على الردود)
        if comment_data.get('is_reply', False):
            logger.debug("⏭️ تخطي الرد لأنه رد على تعليق آخر")
            return False
        
        # يمكنك إضافة شروط أخرى:
        # - عدم الرد على كلمات معينة
        # - الرد فقط إذا كان للتعليق عدد معين من الكلمات
        # - إلخ
        
        return True
