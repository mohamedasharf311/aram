import os
import random
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ReplyManager:
    """إدارة الردود التلقائية"""
    
    def __init__(self):
        # الردود المتنوعة (سيختار البوت رداً عشوائياً)
        self.default_replies = [
            "شكراً لتعليقك! نحن نقدر وقتك. 😊",
            "تسلم على تفاعلك الجميل! نورت الصفحة 🌟",
            "نقدر تواصلك معنا، شكراً جزيلاً! ❤️",
            "تعليقك يعني لنا الكثير، شكراً لمشاركتنا! 🙏",
            "نحن سعداء بتفاعلك، شكراً لك! ✨",
            "شكراً لمشاركتنا رأيك! نتمنى لك يوماً سعيداً 🌹",
            "فخورين بمتابعين زيك! تعليقك أسعدنا 🥰"
        ]
        
        # إضافة الرد من متغير البيئة إذا وجد
        env_reply = os.getenv("REPLY_MESSAGE")
        if env_reply:
            self.default_replies.insert(0, env_reply)
        
        logger.info(f"✅ تم تهيئة مدير الردود بـ {len(self.default_replies)} رد")
    
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
        
        # يمكنك إضافة منطق ذكي هنا بناءً على محتوى التعليق
        if '?' in comment_text or '؟' in comment_text:
            # إذا كان السؤال يحتوي على علامة استفهام
            custom_reply = "شكراً على سؤالك! فريقنا سيتواصل معك قريباً للإجابة عليه 📞"
            return custom_reply
        
        if any(word in comment_text for word in ['شكر', 'تسلم', 'مشكور', 'thanks']):
            # إذا كان التعليق شكراً
            custom_reply = "العفو! هذا واجبنا من أجلك 😊"
            return custom_reply
        
        # اختيار رد عشوائي من القائمة
        reply = random.choice(self.default_replies)
        
        # إضافة اسم المعلق أحياناً (30% احتمال)
        if commenter_name and random.random() < 0.3:
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
        # لا نرد على الردود (لتجنب التكرار)
        if comment_data.get('is_reply', False):
            logger.debug("⏭️ تخطي الرد على رد")
            return False
        
        # يمكن إضافة شروط أخرى هنا
        return True
