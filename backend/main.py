import os
from fastapi import FastAPI, UploadFile, File, Form
from backend.database import Base, engine, SessionLocal
from backend.models import LostItem, FoundItem
from backend.image_generation import generate_lost_item_image
from backend.caption import generate_caption
from backend.embedding import get_combined_embedding
from backend.vector_db import add_to_vector_db, search_vector_db

Base.metadata.create_all(bind=engine)

app = FastAPI()

DISTANCE_THRESHOLD = 0.25  # lower = more similar


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

    if results["ids"] and results["distances"]:
        distance = results["distances"][0][0]
        matched_id = results["ids"][0][0]

        response_data["distance"] = float(distance)

        if distance < DISTANCE_THRESHOLD:
            response_data["match_found"] = True
            response_data["matched_id"] = matched_id

            print(f"🔥 MATCH FOUND with Lost ID {matched_id}")
            print(f"Distance: {distance}")

    return response_data

