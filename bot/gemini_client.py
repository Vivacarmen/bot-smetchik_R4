"""
Отдельный клиент для Gemini API.
Не зависит от прокси, работает напрямую.
"""

import google.generativeai as genai
import os
import logging

class GeminiClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY не задан")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.logger = logging.getLogger(__name__)
    
    async def ask(self, prompt: str, system_prompt: str = None) -> str:
        """
        Отправить запрос к Gemini.
        
        Args:
            prompt: Основной запрос
            system_prompt: Системная инструкция (роль)
        
        Returns:
            Текст ответа или None при ошибке
        """
        try:
            # Gemini не разделяет system/user, объединяем
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    'temperature': 0.1,
                    'max_output_tokens': 4000,
                }
            )
            
            return response.text
            
        except Exception as e:
            self.logger.error(f"Gemini error: {e}")
            return None
    
    def health_check(self) -> bool:
        """Проверка работоспособности"""
        try:
            response = self.model.generate_content("test", {'max_output_tokens': 1})
            return True
        except:
            return False
