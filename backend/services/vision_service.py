"""
Image safety scoring service.
- If GROQ_API_KEY is set in .env → uses Groq Vision API (Llama 3.2 Vision)
- Otherwise → returns deterministic mock scores (for development)
"""

import hashlib
import random
import httpx
import base64
import re
from config import GROQ_API_KEY


async def analyze_image(image_bytes: bytes, filename: str = "") -> dict:
    """Returns { safety_score, vision_labels, status }"""
    print(f"=== Image Analysis Started ===")
    print(f"GROQ_API_KEY exists: {bool(GROQ_API_KEY)}")
    print(f"GROQ_API_KEY length: {len(GROQ_API_KEY) if GROQ_API_KEY else 0}")
    
    if GROQ_API_KEY:
        print("Using Groq Vision API")
        return await _groq_vision(image_bytes)
    else:
        print("Using mock vision (no API key)")
        return _mock_vision(image_bytes, filename)


async def _groq_vision(image_bytes: bytes) -> dict:
    """Analyze image safety using Groq Llama 3.2 Vision model with enhanced accuracy."""
    
    # Resize image if too large (Groq has size limits)
    from PIL import Image
    import io
    
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # Resize if larger than 2048px on any side
        max_size = 2048
        if img.width > max_size or img.height > max_size:
            ratio = min(max_size / img.width, max_size / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert back to bytes
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85)
            image_bytes = output.getvalue()
    except Exception as e:
        print(f"Image resize error: {e}")
        # Continue with original if resize fails
    
    # Convert image to base64
    b64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    # Determine image type
    image_type = "jpeg"
    if image_bytes[:4] == b'\x89PNG':
        image_type = "png"
    elif image_bytes[:3] == b'GIF':
        image_type = "gif"
    elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
        image_type = "webp"
    
    data_url = f"data:image/{image_type};base64,{b64_image}"
    
    # Enhanced safety analysis prompt for better accuracy
    prompt = """You are an expert content moderation AI. Analyze this image thoroughly for safety concerns across multiple dimensions.

For each category below, provide a precise numerical score from 0-100 where:
- 0-20: Safe/Clean content
- 21-40: Slightly concerning but acceptable
- 41-60: Moderately concerning, needs review
- 61-80: Problematic content
- 81-100: Highly inappropriate/dangerous

Categories to evaluate:

1. ADULT CONTENT (nudity, sexual acts, suggestive poses, intimate body parts exposed):
   - Look for exposed private parts, sexual acts, lingerie in suggestive context
   - Consider clothing coverage, poses, and overall context

2. VIOLENCE (weapons, blood, fighting, gore, injuries):
   - Check for visible weapons, fighting scenes, blood, injuries, aggressive actions
   - Real weapons score higher than toys/props

3. HATE SPEECH (racist symbols, extremist content, discriminatory imagery):
   - Nazi symbols, KKK imagery, confederate flags in hate context
   - Slurs, discriminatory signs or gestures

4. DANGEROUS ACTIVITIES (drugs, self-harm, illegal acts, unsafe behaviors):
   - Drug paraphernalia, self-harm tools, dangerous stunts
   - Illegal activities, substance abuse

5. DISTURBING CONTENT (horror, death, graphic content, shocking material):
   - Dead bodies, severe injuries, horrific scenes
   - Extremely scary or psychologically disturbing imagery

Also identify 5-8 main objects, people, activities, or themes you see in the image.

Provide your analysis in this EXACT format (no extra text):
ADULT: [number 0-100]
VIOLENCE: [number 0-100]
HATE: [number 0-100]
DANGEROUS: [number 0-100]
DISTURBING: [number 0-100]
LABELS: [object1, object2, object3, object4, object5]
REASONING: [Brief 1-2 sentence explanation of the overall safety assessment]

BE ACCURATE AND THOROUGH. Examine the image carefully before scoring."""

    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",  # Current Groq vision model (Llama 4 Scout)
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}}
                ]
            }
        ],
        "temperature": 0.1,  # Lower temperature for more consistent results
        "max_completion_tokens": 800
    }
    
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            
            if response.status_code != 200:
                print(f"Groq API error: {response.status_code} - {response.text}")
                return _mock_vision(image_bytes, "")
                
            response.raise_for_status()
            result = response.json()
            
            # Parse the response
            content = result["choices"][0]["message"]["content"]
            
            # Extract scores using regex with better error handling
            adult_match = re.search(r'ADULT:\s*(\d+)', content, re.IGNORECASE)
            violence_match = re.search(r'VIOLENCE:\s*(\d+)', content, re.IGNORECASE)
            hate_match = re.search(r'HATE:\s*(\d+)', content, re.IGNORECASE)
            dangerous_match = re.search(r'DANGEROUS:\s*(\d+)', content, re.IGNORECASE)
            disturbing_match = re.search(r'DISTURBING:\s*(\d+)', content, re.IGNORECASE)
            labels_match = re.search(r'LABELS:\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
            reasoning_match = re.search(r'REASONING:\s*(.+?)(?:\n\n|$)', content, re.IGNORECASE | re.DOTALL)
            
            # Get individual scores with defaults
            adult = min(100, max(0, int(adult_match.group(1)))) if adult_match else 0
            violence = min(100, max(0, int(violence_match.group(1)))) if violence_match else 0
            hate = min(100, max(0, int(hate_match.group(1)))) if hate_match else 0
            dangerous = min(100, max(0, int(dangerous_match.group(1)))) if dangerous_match else 0
            disturbing = min(100, max(0, int(disturbing_match.group(1)))) if disturbing_match else 0
            
            # Enhanced weighted calculation - more emphasis on severe violations
            # Use maximum of weighted average and highest individual score (with dampening)
            weighted_avg = int(
                adult * 0.35 +       # Highest weight for adult content
                violence * 0.30 +    # High weight for violence
                hate * 0.15 +        # Moderate weight for hate speech
                dangerous * 0.15 +   # Moderate weight for dangerous activities
                disturbing * 0.05    # Lower weight as it's often subjective
            )
            
            # Take the higher of weighted average or 70% of the highest category score
            max_individual = max(adult, violence, hate, dangerous, disturbing)
            safety_score = int(max(weighted_avg, max_individual * 0.7))
            
            safety_score = min(100, max(0, safety_score))
            
            # Parse labels
            labels = []
            if labels_match:
                label_text = labels_match.group(1).strip()
                label_list = [l.strip() for l in label_text.split(',')]
                labels = [{"name": label, "confidence": 0.90} for label in label_list[:8] if label]
            
            # Get reasoning
            reasoning = reasoning_match.group(1).strip() if reasoning_match else "Automated safety analysis completed"
            
            status = _score_to_status(safety_score)
            
            return {
                "safety_score": safety_score,
                "vision_labels": labels,
                "status": status,
                "reasoning": reasoning,
                "details": {
                    "adult": adult,
                    "violence": violence,
                    "hate": hate,
                    "dangerous": dangerous,
                    "disturbing": disturbing
                }
            }
            
    except Exception as e:
        # Log error and fallback to mock
        print(f"Groq API error: {e}")
        import traceback
        traceback.print_exc()
        return _mock_vision(image_bytes, "")


async def _real_vision(image_bytes: bytes) -> dict:
    b64 = base64.b64encode(image_bytes).decode()
    payload = {
        "requests": [{
            "image": {"content": b64},
            "features": [
                {"type": "SAFE_SEARCH_DETECTION"},
                {"type": "LABEL_DETECTION", "maxResults": 8},
            ]
        }]
    }
    url = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_VISION_KEY}"
    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.post(url, json=payload)
        res.raise_for_status()

    result = res.json()["responses"][0]
    safe_search = result.get("safeSearchAnnotation", {})
    labels_raw  = result.get("labelAnnotations", [])

    # Compute weighted safety score
    score = 0.0
    for field, weight in SAFE_SEARCH_WEIGHTS.items():
        likelihood = safe_search.get(field, "UNKNOWN")
        score += LIKELIHOOD_SCORE.get(likelihood, 0) * weight

    safety_score = min(100, int(round(score)))

    labels = [
        {"name": l["description"], "confidence": round(l["score"], 3)}
        for l in labels_raw
    ]

    status = _score_to_status(safety_score)
    return {"safety_score": safety_score, "vision_labels": labels, "status": status}


def _mock_vision(image_bytes: bytes, filename: str) -> dict:
    """Deterministic mock: same file always gets same score."""
    digest = hashlib.md5(image_bytes[:512]).hexdigest()
    seed = int(digest[:8], 16)
    rng = random.Random(seed)

    safety_score = rng.randint(0, 100)

    mock_labels = [
        {"name": "Photograph", "confidence": round(rng.uniform(0.85, 0.99), 3)},
        {"name": "Image",      "confidence": round(rng.uniform(0.70, 0.90), 3)},
        {"name": "Person",     "confidence": round(rng.uniform(0.50, 0.85), 3)},
        {"name": "Outdoor",    "confidence": round(rng.uniform(0.40, 0.80), 3)},
    ]

    status = _score_to_status(safety_score)
    return {"safety_score": safety_score, "vision_labels": mock_labels, "status": status}


def _score_to_status(score: int) -> str:
    if score >= 80: return "rejected"
    if score >= 50: return "manual_review"
    return "approved"
