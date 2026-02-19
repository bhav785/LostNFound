import os
from fastapi import FastAPI, UploadFile, File, Form
from database import Base, engine, SessionLocal
from models import LostItem, FoundItem, DetectiveRequest, FinalizeRequest
from image_generation import generate_lost_item_image
from caption import generate_caption    
from embedding import get_combined_embedding
from vector_db import add_to_vector_db, search_vector_db
from fastapi.middleware.cors import CORSMiddleware
import json
import requests
from pydantic import BaseModel
import re

from dotenv import load_dotenv
load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DISTANCE_THRESHOLD = 0.25  # lower = more similar


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def get_root_path():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@app.post("/lost/")
def add_lost(description: str = Form(...)):
    db = SessionLocal()

    image_path = generate_lost_item_image(description)

    lost = LostItem(description=description, image_path=image_path)
    db.add(lost)
    db.commit()
    db.refresh(lost)

    embedding = get_combined_embedding(description, image_path)
    add_to_vector_db(lost.id, embedding)

    db.close()

    return {"message": "Lost item stored successfully"}


@app.post("/found/")
def add_found(file: UploadFile = File(...)):
    db = SessionLocal()

    BASE_DIR = get_root_path()
    UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_images")
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    caption = generate_caption(file_path)

    found = FoundItem(caption=caption, image_path=file_path)
    db.add(found)
    db.commit()

    query_embedding = get_combined_embedding(caption, file_path)

    results = search_vector_db(query_embedding)

    response_data = {
        "caption": caption,
        "match_found": False,
        "matched_id": None,
        "distance": None
    }

    try:
        distance = results["distances"][0][0]
        matched_id = results["ids"][0][0]

        response_data["distance"] = float(distance)

        if distance < DISTANCE_THRESHOLD:
            response_data["match_found"] = True
            response_data["matched_id"] = matched_id

    except (IndexError, KeyError, TypeError):
        # No matches found
        pass

    return response_data


@app.post("/api/detective")
def detective(data: DetectiveRequest):
    try:
        history = data.history
        user_input = data.userInput

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

        conversation = "\n".join([h["content"] for h in history])

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{conversation}\n{user_input}"}
                ],
                "temperature": 0.7,
                "max_tokens": 200
            }
        )

        result = response.json()
        content = result["choices"][0]["message"]["content"]
        print("RAW CONTENT:", content)


        # Remove markdown code blocks if present
        cleaned = re.sub(r"```json|```", "", content).strip()

        parsed = json.loads(cleaned)
        return parsed

            

    except Exception as e:
        print("Detective Error:", e)
        return {
        "text": f"Backend error: {str(e)}",
        "tags": [],
        "confidenceDelta": 0
    }


@app.post("/api/detective/finalize")
def finalize_description(data: FinalizeRequest):
    try:
        history = data.history

        system_prompt = """
You are generating a final structured item description.

Based ONLY on information mentioned in the conversation,
write a detailed physical description of the lost item.

Include:
- Category 
- Color
- Material (if mentioned)
- Shape (if mentioned)
- Distinctive features (if mentioned)

Do NOT ask questions.
Do NOT invent details.
Return only the description paragraph.
"""

        messages = [{"role": "system", "content": system_prompt}]

        for h in history[-8:]:
            messages.append({
                "role": h["role"],
                "content": h["content"]
            })

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 150
            }
        )

        result = response.json()
        final_text = result["choices"][0]["message"]["content"].strip()

        return {"final_description": final_text}

    except Exception as e:
        print("Finalize Error:", e)
        return {"final_description": ""}


