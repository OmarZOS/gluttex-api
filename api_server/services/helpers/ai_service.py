# services/ai_service.py
import json
import base64
from typing import Dict, Any
from datetime import datetime
from core.models.api_models import Iproduct_API
from communication.ai.openai.gpt import call_openai_vision, call_openai

class AIService:
    """Service for AI-powered product recognition and information"""
    
    async def recognize_product_from_image(self, image_bytes: bytes, language: str = "fr") -> tuple[Dict[str, Any], str]:
        """Recognize product from image using AI vision"""
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        messages = [
            {
                "role": "system",
                "content": (
                    "Identify product in image. Return JSON only: "
                    "{name, brand, barcode, confidence, gluten_status, source}. "
                    "gluten_status ∈ [gluten_free, contains_gluten, may_contain_gluten, unknown]. "
                    "If unclear, estimate from packaging. No extra text. "
                    f"Language: {language}."
                )
            },
            {
                "role": "user",
                "content": "Analyze and search for this product and return ONLY the JSON {name, brand, barcode, confidence, gluten_status, info_source}, confidence is a decimal."
            }
        ]

        try:
            result, model = await call_openai_vision(
                messages=messages,
                images=[image_b64],
                model_detail_percentage=0.6,
                json_mode=True,
                max_tokens=200,
                temperature=0.1
            )
            json_result = json.loads(result)
        except Exception as e:
            print(f"[IMAGE RECOGNITION ERROR] {e}")
            return self._get_fallback_response(str(e)), "error"
        
        return json_result, model
    
    async def generate_product_info_by_barcode(self, barcode: str, language: str = "fr") -> tuple[Dict[str, Any], str]:
        """Generate product information from barcode using AI"""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a product database. "
                    "Barcode → JSON only: "
                    "{name, brand, description, price_DA, gluten_status, image_url}. "
                    "price_DA is an integer in Algerian dinar. "
                    "confidence is a decimal. "
                    "gluten_status ∈ [gluten_free, contains_gluten, may_contain_gluten, unknown]. "
                    "If product not found, estimate from similar products. "
                    f"Language: {language}. No other text."
                )
            },
            {
                "role": "user",
                "content": f"Barcode {barcode}. Return ONLY JSON (name, brand, barcode, confidence, gluten_status, info_source), confidence is a decimal."
            }
        ]

        try:
            result, model = await call_openai(
                messages=messages,
                model_detail_percentage=0.7,
                json_mode=True,
                max_tokens=250,
                temperature=0.1
            )
            print(f"[RESULT]: {result}")
            json_result = json.loads(result)
        except Exception as e:
            print(f"[BARCODE LOOKUP ERROR] {e}")
            return self._get_fallback_response(str(e)), "error"
        
        return json_result, model
    
    def format_ai_result_to_iproduct(self, ai_result: Dict[str, Any], model_name: str) -> Iproduct_API:
        """Convert AI recognition result to Iproduct_API format"""
        now = datetime.now().isoformat()
        
        return Iproduct_API(
            id_iproduct=None,
            iproduct_name=ai_result.get('name'),
            iproduct_barcode=ai_result.get('barcode'),
            iproduct_brand=ai_result.get('brand'),
            iproduct_estimated_price=ai_result.get('price_DA'),
            iproduct_price_currency="DZD",
            iproduct_gluten_status=ai_result.get('gluten_status', 'unknown'),
            iproduct_info_source=model_name,
            iproduct_info_confidence=ai_result.get('confidence', 0.0),
            iproduct_last_price_update=now,
            iproduct_created_at=now,
            iproduct_last_update=now,
            iproduct_model_name=model_name,
            iproduct_image_url=None
        )
    
    def _get_fallback_response(self, error_message: str = "") -> Dict[str, Any]:
        """Return fallback response when AI fails"""
        return {
            "error": error_message,
            "name": "Unknown",
            "brand": "Unknown",
            "category": "Unknown",
            "confidence": 0,
            "gluten_status": "unknown",
            "price_DA": 0.0,
            "source": "fallback"
        }
    
    def clean_json_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from AI response with fallback"""
        import re
        
        try:
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
        
        return self._get_fallback_response()