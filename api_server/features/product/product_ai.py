



from communication.ai.openai.gpt import *
import base64


async def ai_recognize_product_from_image(image_bytes: bytes, language="fr") -> Dict[str, Any]:
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    messages = [
        {
            "role": "system",
            "content": (
                "Identify product in image. Return JSON only: "
                "{name, brand, barcode, confidence, gluten_status,source}. "
                "gluten_status ∈ [gluten_free, contains_gluten, may_contain_gluten, unknown]. "
                "If unclear, estimate from packaging. No extra text. "
                f"Language: {language}."
            )
        },
        {
            "role": "user",
            "content": "Analyze and search for this product and return ONLY the JSON {name, brand, barcode, confidence, gluten_status,info_source}."
        }
    ]

    try:
        result,model = await call_openai_vision(
            messages=messages,
            images=[image_b64],
            model_detail_percentage=0.6,
            json_mode=True,
            max_tokens=200,
            temperature=0.1
        )
        json_result =  json.loads(result)
    except Exception as e:
        print(f"[IMAGE RECOGNITION ERROR] {e}")
        return {
            "error": str(e),
            "name": "Unknown",
            "brand": "Unknown",
            "category": "Unknown",
            "confidence": 0,
            "gluten_status": "unknown"
        }
    return json_result

async def ai_generate_product_info_by_barcode(barcode: str, language="fr") -> Dict[str, Any]:

    messages = [
        {
            "role": "system",
            "content": (
                "You are a product database. "
                "Barcode → JSON only: "
                "{name, brand, description, price_DA, gluten_status,image_url}. "
                "price_DA is an integer in Algerian dinar. "
                "gluten_status ∈ [gluten_free, contains_gluten, may_contain_gluten, unknown]. "
                "If product not found, estimate from similar products. "
                f"Language: {language}. No other text."
            )
        },
        {
            "role": "user",
            "content": f"Barcode {barcode}. Return ONLY JSON (name, brand, barcode, confidence, gluten_status,info_source)."
        }
    ]

    try:
        result,model = await call_openai(
            messages=messages,
            model_detail_percentage=0.7,
            json_mode=True,
            max_tokens=250,
            temperature=0.1
        )
        print(f"[RESULT]: {result}")
        json_result =  json.loads(result)
    except Exception as e:
        print(f"[BARCODE LOOKUP ERROR] {e}")
        return {
            "error": str(e),
            "name": "Unknown",
            "brand": "Unknown",
            "category": "Unknown",
            "description": "Not available",
            "price_DA": None,
            "gluten_status": "unknown"
        }
    return json_result










