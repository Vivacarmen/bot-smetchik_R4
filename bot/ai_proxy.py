import httpx
import json
import logging
import time
import os
import socket
from bot import config

class AIClient:
    """
    Универсальный клиент для AI API (Groq, OpenRouter, резервные провайдеры).
    Поддержка SOCKS5 прокси (Xray) для обхода блокировок при необходимости.
    """
    
    # Настройки прокси (Xray на порту 10808)
    PROXY_URL = "socks5://127.0.0.1:10808"
    PROXY_HOST = "127.0.0.1"
    PROXY_PORT = 10808
    
    def __init__(self, api_key=None, provider="groq", use_proxy=False):
        self.api_key = api_key if api_key else config.GROQ_API_KEY
        self.provider = provider
        self.use_proxy = use_proxy  # Включается при необходимости
        
        # Настройки для разных провайдеров
        self.providers = {
            "groq": {
                "url": "https://api.groq.com/openai/v1/chat/completions",
                "models": ["llama-3.1-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"],
                "headers": {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            },
            "openrouter": {
                "url": "https://openrouter.ai/api/v1/chat/completions",
                "models": ["anthropic/claude-3.5-sonnet", "openai/gpt-4o-mini"],
                "headers": {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://r4project.ru",
                    "X-Title": "Teambuilding Bot"
                }
            }
        }
        
        # Логирование
        self.log_file = os.path.join(config.LOG_PATH, "ai_error_log.txt")
        os.makedirs(config.LOG_PATH, exist_ok=True)

    def _write_debug_log(self, message):
        """Сохранение детальной ошибки для анализа."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")

    def _is_proxy_alive(self):
        """Проверка, поднят ли SOCKS5 туннель Xray."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            try:
                s.connect((self.PROXY_HOST, self.PROXY_PORT))
                return True
            except (socket.timeout, ConnectionRefusedError):
                return False

    async def ask(self, prompt: str, system_prompt=None):
        """
        Отправка запроса к AI с fallback на резервные модели.
        """

        if self.provider == "gemini":
    return await self._ask_gemini(prompt, system_prompt)

        if not self.api_key:
            self._write_debug_log("ERROR: API Key is missing in config")
            return None

        # Проверка прокси если включён
        if self.use_proxy and not self._is_proxy_alive():
            self._write_debug_log("PROXY WARNING: Port 10808 is closed. Trying without proxy...")
            self.use_proxy = False

        # Стандартная системная инструкция
        if system_prompt is None:
            system_prompt = """Ты — Senior Event Producer с 10-летним опытом в ивент-индустрии.
Твоя задача — создавать профессиональные сметы на корпоративные мероприятия.
Отвечай структурированно, используй точные цены из базы знаний."""

        # Пробуем модели по порядку
        provider_config = self.providers.get(self.provider, self.providers["groq"])
        models = provider_config["models"]
        
        for model in models:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 4000,
                "top_p": 0.95
            }

            # Настройка клиента (с прокси или без)
            client_kwargs = {"timeout": 60.0}
            if self.use_proxy:
                client_kwargs["proxy"] = self.PROXY_URL

            try:
                async with httpx.AsyncClient(**client_kwargs) as client:
                    response = await client.post(
                        provider_config["url"],
                        json=payload,
                        headers=provider_config["headers"]
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        try:
                            text = result['choices'][0]['message']['content']
                            return text
                        except (KeyError, IndexError) as e:
                            self._write_debug_log(f"JSON Structure Error ({model}): {str(e)}")
                            continue
                    
                    error_msg = f"API Error ({model}): {response.status_code} - {response.text}"
                    self._write_debug_log(error_msg)
                    
            except httpx.TimeoutException:
                self._write_debug_log(f"TIMEOUT ({model}): Request exceeded 60s")
                continue
            except Exception as e:
                self._write_debug_log(f"Request Exception ({model}): {str(e)}")
                continue
        
        self._write_debug_log("ERROR: All models failed. No response generated.")
        return None

    async def health_check(self):
        """Проверка доступности API."""
        try:
            client_kwargs = {"timeout": 10.0}
            if self.use_proxy:
                client_kwargs["proxy"] = self.PROXY_URL
                
            async with httpx.AsyncClient(**client_kwargs) as client:
                test_payload = {
                    "model": self.providers[self.provider]["models"][0],
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 1
                }
                response = await client.post(
                    self.providers[self.provider]["url"],
                    json=test_payload,
                    headers=self.providers[self.provider]["headers"]
                )
                return response.status_code == 200
        except:
            return False

    async def _ask_gemini(self, prompt, system_prompt):
    import google.generativeai as genai
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    response = model.generate_content(full_prompt)
    return response.text
