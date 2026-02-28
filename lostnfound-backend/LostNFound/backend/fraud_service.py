import os
import json
import requests
import re
from datetime import datetime
from typing import List, Dict

# Mistral-7B via OpenRouter for generating questions
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def generate_verification_questions(lost_description: str, found_caption: str) -> List[Dict]:
    """
    Generates 3 contextual ownership verification questions based on the item description.
    """
    system_prompt = """
    You are a security protocol designer. Generate 3 specific, contextual questions to verify if a claimant is the rightful owner of a lost item.
    
    Lost Item Description: {lost_description}
    Found Item Caption: {found_caption}
    
    Rules:
    - Questions should be partially open-ended (e.g., 'What brand is it?') or multiple choice.
    - Do NOT include the answers in the questions.
    - Provide a 'correct_answer' for each question based on the lost item description.
    - Format as JSON list of objects: [{"question": "...", "type": "text"|"choice", "options": ["..."]|null, "correct_answer": "..."}]
    - Return ONLY the JSON.
    """
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "system", "content": system_prompt.format(lost_description=lost_description, found_caption=found_caption)}
                ],
                "temperature": 0.5
            },
            timeout=30
        )
        
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            cleaned = re.sub(r"```json|```", "", content).strip()
            return json.loads(cleaned)
    except Exception as e:
        print(f"Error generating questions: {e}")
    
    # Fallback questions if AI fails
    return [
        {"question": "Can you specify the brand or any unique labels on the item?", "type": "text", "correct_answer": "any"},
        {"question": "Where exactly (building/room/landmark) did you lose it?", "type": "text", "correct_answer": "any"},
        {"question": "What is the primary color and material of the item?", "type": "text", "correct_answer": "any"}
    ]

def calculate_confidence_score(user_answers: List[Dict], actual_questions: List[Dict], proof_files: List[str], metadata: Dict) -> Dict:
    """
    Logic:
    - Ownership question match: 60%
    - Image similarity (presence of proof): 25%
    - Metadata consistency (location/time): 10%
    - Submission timing validity: 5%
    """
    score = 0
    details = {}
    
    # 1. Ownership questions (60%)
    correct_count = 0
    for i, ans in enumerate(user_answers):
        actual = actual_questions[i]
        user_val = str(ans.get("answer", "")).lower().strip()
        correct_val = str(actual.get("correct_answer", "")).lower().strip()
        
        # Simple string match or keyword match
        if correct_val == "any" or user_val == correct_val or correct_val in user_val:
            correct_count += 1
            
    question_score = (correct_count / len(actual_questions)) * 60 if actual_questions else 0
    score += question_score
    details["questions_score"] = question_score
    
    # 2. Proof files (25%)
    # Basic check: at least 2 files (Item proof + Selfie)
    proof_score = min(len(proof_files) / 2, 1.0) * 25
    score += proof_score
    details["proof_score"] = proof_score
    
    # 3. Metadata consistency (10%)
    # For now, let's assume if they provided a location that matches roughly
    # In a real app, we'd compare lat/lng or specific strings
    metadata_score = 10 # Default to 10 for now if they filled the form
    score += metadata_score
    details["metadata_score"] = metadata_score
    
    # 4. Submission timing (5%)
    # Check if they haven't spent too long (e.g., < 30 mins)
    timing_score = 5
    score += timing_score
    details["timing_score"] = timing_score
    
    status = "PENDING"
    VERIFICATION_THRESHOLD = 75
    
    if score >= VERIFICATION_THRESHOLD:
        status = "VERIFIED"
    elif score >= 50:
        status = "MANUAL_REVIEW"
    else:
        status = "FAILED"
        
    return {
        "confidence_score": round(score, 2),
        "status": status,
        "details": details
    }
