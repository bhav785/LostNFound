import torch
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

# Load models once
text_model = SentenceTransformer("all-MiniLM-L6-v2")
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model.eval()


def get_text_embedding(text):
    return text_model.encode(text).tolist()


def get_image_embedding(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = clip_processor(images=image, return_tensors="pt")

    with torch.no_grad():
        # 1. Use get_image_features to get image-only embeddings
        outputs = clip_model.get_image_features(pixel_values=inputs["pixel_values"])
        
        # 2. Extract the raw tensor (some versions return an object)
        image_features = outputs.pooler_output if hasattr(outputs, 'pooler_output') else outputs

    # 3. Normalize for accurate similarity comparison
    image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)

    return image_features.squeeze().cpu().numpy().tolist()

def get_combined_embedding(text, image_path):
    text_emb = np.array(get_text_embedding(text))
    image_emb = np.array(get_image_embedding(image_path))

    # Ensure both are normalized before concatenation if you plan to use them for vector search
    combined = np.concatenate([text_emb, image_emb])
    
    # Optional: Re-normalize the entire combined vector
    combined = combined / np.linalg.norm(combined)

    return combined.tolist()
