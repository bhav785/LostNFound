import os
import time
from fastapi import FastAPI, UploadFile, File, Form
from database import Base, engine, SessionLocal
from models import LostItem, FoundItem, DetectiveRequest, FinalizeRequest, Match, Verification
from image_generation import generate_lost_item_image
from caption import generate_caption    
from embedding import get_combined_embedding
from vector_db import add_to_vector_db, search_vector_db
from fastapi.middleware.cors import CORSMiddleware
import json
import requests
from pydantic import BaseModel
import re
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fraud_service import generate_verification_questions, calculate_confidence_score
from qr_utility import generate_signed_qr
import uuid
import shutil
from fastapi import HTTPException


from dotenv import load_dotenv
load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development integration
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(BASE_DIR, "generated_images")

app.mount("/generated_images", StaticFiles(directory=IMAGE_DIR), name="generated_images")

UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_images")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploaded_images", StaticFiles(directory=UPLOAD_DIR), name="uploaded_images")

VERIFICATION_DIR = os.path.join(UPLOAD_DIR, "verification")
os.makedirs(VERIFICATION_DIR, exist_ok=True)

QR_DIR = os.path.join(BASE_DIR, "qr_codes")
os.makedirs(QR_DIR, exist_ok=True)
app.mount("/qr_codes", StaticFiles(directory=QR_DIR), name="qr_codes")


DISTANCE_THRESHOLD = 0.25  # lower = more similar


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def get_root_path():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@app.post("/lost/")
def add_lost(description: str = Form(...), email: str = Form(...)):
    db = SessionLocal()

    image_path = generate_lost_item_image(description)
    if not image_path:
        db.close()
        return {"success": False, "message": "Image generation failed"}

    lost = LostItem(
        description=description, 
        image_path=image_path, 
        email=email,
        created_at=datetime.now().isoformat()
    )
    db.add(lost)
    db.commit()
    db.refresh(lost)

    embedding = get_combined_embedding(description, image_path)
    add_to_vector_db(lost.id, embedding)

    # Trigger matching
    match_found = check_for_matches(lost.id, embedding, is_lost=True)

    db.close()

    image_url = f"http://localhost:8000/generated_images/{os.path.basename(image_path)}"

    return {
        "success": True,
        "message": "Lost item stored successfully",
        "image_url": image_url,
        "match_found": match_found
    }



@app.post("/found/")
def add_found(
    file: UploadFile = File(...), 
    location: str = Form(...), 
    condition: str = Form(...)
):
    db = SessionLocal()

    BASE_DIR = get_root_path()
    UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_images")
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    caption = generate_caption(file_path)

    found = FoundItem(
        caption=caption, 
        image_path=file_path,
        location=location,
        condition=condition,
        created_at=datetime.now().isoformat()
    )
    db.add(found)
    db.commit()
    db.refresh(found)

    query_embedding = get_combined_embedding(caption, file_path)
    add_to_vector_db(found.id, query_embedding, is_lost=False)

    # Matching logic for found items
    match_found = check_for_matches(found.id, query_embedding, is_lost=False)

    db.close()

    return {
        "success": True,
        "caption": caption,
        "match_found": match_found,
        "item_id": found.id
    }

@app.get("/found-items")
def get_found_items():
    db = SessionLocal()
    items = db.query(FoundItem).order_by(FoundItem.id.desc()).all()
    result = []
    for item in items:
        # Assuming uploaded images are also servable or moved to a static dir
        # Let's mount uploaded_images too
        result.append({
            "id": item.id,
            "caption": item.caption,
            "image_url": f"http://localhost:8000/uploaded_images/{os.path.basename(item.image_path)}",
            "location": item.location,
            "date": item.created_at
        })
    db.close()
    return result

def check_for_matches(item_id, embedding, is_lost=True):
    db = SessionLocal()
    match_found = False
    
    try:
        # If is_lost=True (new lost item), search FOUND collection (search_lost=False)
        # If is_lost=False (new found item), search LOST collection (search_lost=True)
        results = search_vector_db(embedding, search_lost=(not is_lost))
        
        if not results["ids"] or not results["ids"][0]:
            return False

        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i]
            matched_id = int(results["ids"][0][i])
            similarity = 1 - distance
            
            if similarity >= 0.6:
                # We have a potential match!
                if is_lost:
                    # We just added a lost item, matched_id is a found item
                    lost_item = db.query(LostItem).filter(LostItem.id == item_id).first()
                    found_item = db.query(FoundItem).filter(FoundItem.id == matched_id).first()
                else:
                    # We just added a found item, matched_id is a lost item
                    lost_item = db.query(LostItem).filter(LostItem.id == matched_id).first()
                    found_item = db.query(FoundItem).filter(FoundItem.id == item_id).first()

                if lost_item and found_item:
                    # Check if match already exists
                    existing_match = db.query(Match).filter(
                        Match.lost_item_id == lost_item.id,
                        Match.found_item_id == found_item.id
                    ).first()
                    
                    if not existing_match:
                        lost_item.matched = 1
                        found_item.matched = 1
                        
                        new_match = Match(
                            lost_item_id=lost_item.id,
                            found_item_id=found_item.id,
                            similarity_score=int(similarity * 100),
                            created_at=datetime.now().isoformat()
                        )
                        db.add(new_match)
                        db.commit()
                        db.refresh(new_match)
                        
                        send_match_email(lost_item.email, lost_item, found_item, new_match.id)
                        match_found = True
                    else:
                        # Existing match found, we skip creating a new one and sending email
                        # But we still mark match_found as True for the response if needed
                        # (The request asks to send email ONLY when a new match is created)
                        match_found = True
                        
    except Exception as e:
        print(f"Matching error: {e}")
    finally:
        db.close()
        
    return match_found

def send_match_email(to_email, lost_item, found_item, match_id):

    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not smtp_user or not smtp_pass:
        print(f"Email skip: Credentials missing. Match for {to_email}")
        return

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    subject = "Your missing item may have been found!"
    body = f"""
    Hello,
    
    Good news! Sherlock has found a potential match for your lost item.
    
    Lost Description: {lost_item.description}
    Matched Found Item: {found_item.caption}
    Location Found: {found_item.location}
    
    You can verify this match here: {frontend_url}/verify/{match_id}
    
    Best,
    LostNFound Team
    """

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.get("/api/verify/start/{match_id}")
def start_verification(match_id: int):
    db = SessionLocal()
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        db.close()
        return {"success": False, "message": "Match not found"}
    
    # Check if verification already exists
    verification = db.query(Verification).filter(Verification.match_id == match_id).first()
    if not verification:
        lost_item = db.query(LostItem).filter(LostItem.id == match.lost_item_id).first()
        found_item = db.query(FoundItem).filter(FoundItem.id == match.found_item_id).first()
        
        # Generate dynamic questions
        questions = generate_verification_questions(lost_item.description, found_item.caption)
        
        verification = Verification(
            match_id=match_id,
            questions_json=questions,
            status="PENDING"
        )
        db.add(verification)
        db.commit()
        db.refresh(verification)
    
    db.close()
    return {
        "success": True,
        "questions": verification.questions_json,
        "status": verification.status
    }

@app.post("/api/verify/submit/{match_id}")
def submit_verification(
    match_id: int,
    answers: str = Form(...),
    item_proof: UploadFile = File(...),
    selfie: UploadFile = File(...)
):
    db = SessionLocal()
    match = db.query(Match).filter(Match.id == match_id).first()
    verification = db.query(Verification).filter(Verification.match_id == match_id).first()
    
    if not match or not verification:
        db.close()
        return {"success": False, "message": "Verification session not found"}

    if verification.status in ["VERIFIED", "FAILED"] and verification.attempt_count >= 3:
        db.close()
        return {"success": False, "message": "Maximum attempts reached"}

    # Save files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    proof_paths = []
    
    for file, prefix in [(item_proof, "proof"), (selfie, "selfie")]:
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"{match_id}_{prefix}_{timestamp}{file_ext}"
        file_path = os.path.join(VERIFICATION_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        proof_paths.append(file_path)

    # Process answers
    try:
        user_answers = json.loads(answers)
    except:
        db.close()
        return {"success": False, "message": "Invalid answers format"}

    # Scoring
    result = calculate_confidence_score(
        user_answers, 
        verification.questions_json, 
        proof_paths, 
        {}
    )

    verification.confidence_score = result["confidence_score"]
    verification.status = result["status"]
    verification.proof_files = proof_paths
    verification.attempt_count += 1
    verification.verification_timestamp = datetime.now().isoformat()

    if verification.status == "VERIFIED":
        # Generate QR
        qr_filename, _ = generate_signed_qr(match.found_item_id, str(uuid.uuid4()), QR_DIR)
        verification.qr_code_path = qr_filename
        match.verified = 1

    db.commit()
    
    res = {
        "success": True,
        "confidence_score": verification.confidence_score,
        "status": verification.status,
        "message": f"Verification {verification.status}"
    }
    
    if verification.status == "VERIFIED":
        res["qr_url"] = f"http://localhost:8000/qr_codes/{verification.qr_code_path}"

    db.close()
    return res

@app.get("/api/verify/status/{match_id}")
def get_verification_status(match_id: int):
    db = SessionLocal()
    verification = db.query(Verification).filter(Verification.match_id == match_id).first()
    
    if not verification:
        db.close()
        return {"success": False, "message": "No verification found"}
    
    res = {
        "success": True,
        "status": verification.status,
        "confidence_score": verification.confidence_score
    }
    
    if verification.qr_code_path:
        res["qr_url"] = f"http://localhost:8000/qr_codes/{verification.qr_code_path}"
    
    db.close()
    return res

@app.get("/api/verify/{match_id}")
def verify_match_legacy(match_id: int):
    # This is the old endpoint, we can keep it as a shortcut or redirect
    return verify_match(match_id)

def verify_match(match_id: int):
    db = SessionLocal()
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        db.close()
        return {"success": False, "message": "Match not found"}
    
    match.verified = 1
    
    lost_item = db.query(LostItem).filter(LostItem.id == match.lost_item_id).first()
    found_item = db.query(FoundItem).filter(FoundItem.id == match.found_item_id).first()
    
    # Also mark items as matched if not already
    lost_item.matched = 1
    found_item.matched = 1
    
    db.commit()
    
    result = {
        "success": True,
        "match": {
            "id": match.id,
            "similarity": match.similarity_score,
            "lost_description": lost_item.description,
            "found_caption": found_item.caption,
            "found_location": found_item.location,
            "found_image_url": f"http://localhost:8000/uploaded_images/{os.path.basename(found_item.image_path)}"
        }
    }
    db.close()
    return result


def call_openrouter(payload, retries=3):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    for attempt in range(retries):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()

            # If model not available or provider error → retry
            if response.status_code >= 500:
                time.sleep(2 ** attempt)
                continue

            # For 4xx errors → stop immediately
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )

        except requests.exceptions.RequestException:
            time.sleep(2 ** attempt)

    raise HTTPException(status_code=500, detail="Model failed after retries")


# -----------------------------
# Main Endpoint
# -----------------------------
@app.post("/api/detective")
def detective(data: DetectiveRequest):

    history = data.history or []
    user_input = data.userInput or ""

    system_prompt = """
You are Sherlock, a detective helping users describe lost items on lostNfound.

Rules:
- Ask ONE short question.
- Extract 1-2 tags.
- Estimate confidenceDelta (1-10).

Respond ONLY in JSON:
{
  "text": "...",
  "tags": ["..."],
  "confidenceDelta": 5
}
"""

    # Merge system + conversation + user into ONE user message
    conversation = "\n".join([h.get("content", "") for h in history])

    combined_prompt = f"""
{system_prompt}

Conversation so far:
{conversation}

User:
{user_input}
"""

    primary_model = "google/gemma-7b-it:free"
    fallback_model = "openrouter/free"

    payload = {
        "model": primary_model,
        "messages": [
            {"role": "user", "content": combined_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }

    # -----------------------------
    # Try Primary Model
    # -----------------------------
    try:
        result = call_openrouter(payload)
    except:
        # Fallback model
        payload["model"] = fallback_model
        result = call_openrouter(payload)

    if "choices" not in result:
        raise HTTPException(status_code=500, detail="Invalid LLM response")

    content = result["choices"][0]["message"]["content"]

    # Remove markdown JSON wrappers if present
    cleaned = re.sub(r"```json|```", "", content).strip()

    if not cleaned:
        raise HTTPException(
            status_code=500,
            detail="Model returned empty response"
        )

    # Try to extract JSON block if model added extra text
    json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)

    if not json_match:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "No JSON found in model response",
                "raw_content": content
            }
        )

    json_text = json_match.group()

    try:
        parsed = json.loads(json_text)
        return parsed
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Invalid JSON format from model",
                "raw_content": content
            }
        )


#no api based description generation
@app.post("/api/detective/finalize")
def finalize_description(data: FinalizeRequest):
    try:
        history = data.history

        if not history:
            return {"final_description": "No conversation data provided."}

        # Collect only USER messages
        user_text = ""
        for h in history:
            if h.get("role") == "user":
                user_text += h.get("content", "") + " "

        user_text = user_text.strip()

        # -----------------------------
        # CATEGORY EXTRACTION
        # First noun-like word after "a" or "an"
        # -----------------------------
        category_match = re.search(r"\b(a|an)\s+([a-zA-Z\s]+?)(?:\.|,|\s)", user_text.lower())
        category = None
        if category_match:
            category = category_match.group(2).split()[0].capitalize()

        # Fallback: first meaningful word
        if not category:
            words = user_text.split()
            if words:
                category = words[0].capitalize()

        # -----------------------------
        # COLOR DETECTION
        # -----------------------------
        common_colors = [
            "black", "white", "blue", "red", "green",
            "yellow", "pink", "purple", "brown",
            "gold", "rose gold", "silver", "grey"
        ]

        color_found = []
        for color in common_colors:
            if color in user_text.lower():
                color_found.append(color.title())

        # -----------------------------
        # MATERIAL DETECTION
        # -----------------------------
        materials = [
            "leather", "metal", "plastic", "gold",
            "silver", "cotton", "denim", "wood",
            "glass", "crystal", "rubber"
        ]

        material_found = []
        for material in materials:
            if material in user_text.lower():
                material_found.append(material.title())

        # -----------------------------
        # SIZE / SHAPE
        # -----------------------------
        size_words = ["small", "large", "big", "tiny", "mini", "dainty"]
        size_found = []
        for word in size_words:
            if word in user_text.lower():
                size_found.append(word.capitalize())

        # -----------------------------
        # LOCATION EXTRACTION
        # -----------------------------
        location = None
        location_match = re.search(
            r"(last saw it|last seen|lost it|left it)\s+(in|at)\s+([a-zA-Z0-9\s]+)",
            user_text.lower()
        )
        if location_match:
            location = location_match.group(3).strip().capitalize()

        # -----------------------------
        # BUILD FINAL DESCRIPTION
        # -----------------------------
        description_parts = []

        if category:
            description_parts.append(f"Category: {category}.")

        if color_found:
            description_parts.append(f"Color: {', '.join(color_found)}.")

        if material_found:
            description_parts.append(f"Material: {', '.join(material_found)}.")

        if size_found:
            description_parts.append(f"Size/Appearance: {', '.join(size_found)}.")

        if location:
            description_parts.append(f"Last seen at: {location}.")

        final_description = " ".join(description_parts)

        if not final_description:
            final_description = "Insufficient details provided to generate description."

        return {"final_description": final_description}

    except Exception as e:
        print("Finalize Endpoint Error:", str(e))
        return {"final_description": "Something went wrong."}
# @app.post("/api/detective/finalize")
# def finalize_description(data: FinalizeRequest):
#     try:
#         history = data.history

#         if not history:
#             print("Finalize Debug: No history received.")
#             return {"final_description": "No conversation data provided."}

#         # ===== SYSTEM PROMPT =====
#         system_prompt = """
# You are generating a final structured item description.

# Based ONLY on information mentioned in the conversation,
# write a detailed physical description of the lost item.

# Include:
# - Category
# - Color
# - Material (if mentioned)
# - Shape (if mentioned)
# - Distinctive features (if mentioned)

# Do NOT ask questions.
# Do NOT invent details.
# Return only the description paragraph.
# """

#         # ===== Convert Entire Conversation To ONE User Message =====
#         conversation_text = ""

#         for h in history:
#             role = h.get("role", "")
#             content = h.get("content", "")

#             print(f"History -> Role: {role}, Content: {content}")

#             conversation_text += f"{role.upper()}: {content}\n"

#         messages = [
#             {"role": "system", "content": system_prompt},
#             {
#                 "role": "user",
#                 "content": f"Here is the conversation:\n\n{conversation_text}\n\nGenerate the final structured description."
#             }
#         ]

#         print("Messages Sent To OpenRouter:")
#         print(messages)

#         # ===== API CALL =====
#         response = requests.post(
#             "https://openrouter.ai/api/v1/chat/completions",
#             headers={
#                 "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#                 "Content-Type": "application/json"
#             },
#             json={
#                 "model": "google/gemma-3-12b-it:free",
#                 "messages": messages,
#                 "temperature": 0.5,
#                 "max_tokens": 200
#             },
#             timeout=30
#         )

#         print("OpenRouter Status Code:", response.status_code)

#         if response.status_code != 200:
#             print("OpenRouter HTTP Error:", response.text)
#             return {"final_description": "AI service error. Try again."}

#         result = response.json()
#         print("OpenRouter Raw Response:", result)

#         if "choices" not in result or not result["choices"]:
#             print("Invalid OpenRouter response structure.")
#             return {"final_description": "AI temporarily unavailable."}

#         final_text = result["choices"][0]["message"]["content"]

#         if final_text:
#             final_text = final_text.strip()

#         if not final_text:
#             print("Model returned empty content.")
#             final_text = "Description could not be generated. Please try again."

#         print("Final Description Generated:", final_text)

#         return {"final_description": final_text}

#     except Exception as e:
#         print("Finalize Endpoint Error:", str(e))
#         return {"final_description": "Something went wrong."}


