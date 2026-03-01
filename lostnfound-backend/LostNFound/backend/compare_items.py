import torch
from PIL import Image
from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# -----------------------------
# Load Models
# -----------------------------
print("Loading models...")
text_model = SentenceTransformer('all-MiniLM-L6-v2')
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model.eval()

def get_tensor(output):
    """Helper to extract raw tensor from ModelOutput objects if necessary."""
    if hasattr(output, 'pooler_output'):
        return output.pooler_output
    if hasattr(output, 'last_hidden_state'):
        return output.last_hidden_state[:, 0, :] # Use CLS token
    return output

def text_similarity(text1, text2):
    emb1 = text_model.encode(text1)
    emb2 = text_model.encode(text2)
    return cosine_similarity([emb1], [emb2])[0][0]

def image_similarity(img_path1, img_path2):
    img1 = Image.open(img_path1).convert("RGB")
    img2 = Image.open(img_path2).convert("RGB")
    
    in1 = clip_processor(images=img1, return_tensors="pt")
    in2 = clip_processor(images=img2, return_tensors="pt")

    with torch.no_grad():
        # Get features and force them to Tensors
        emb1 = get_tensor(clip_model.get_image_features(**in1))
        emb2 = get_tensor(clip_model.get_image_features(**in2))

    # Normalize
    emb1 /= emb1.norm(p=2, dim=-1, keepdim=True)
    emb2 /= emb2.norm(p=2, dim=-1, keepdim=True)
    
    return torch.matmul(emb1, emb2.T).item()

def text_image_similarity(text, img_path):
    img = Image.open(img_path).convert("RGB")
    inputs = clip_processor(text=[text], images=img, return_tensors="pt", padding=True)

    with torch.no_grad():
        t_emb = get_tensor(clip_model.get_text_features(input_ids=inputs['input_ids'], attention_mask=inputs['attention_mask']))
        i_emb = get_tensor(clip_model.get_image_features(pixel_values=inputs['pixel_values']))

    t_emb /= t_emb.norm(p=2, dim=-1, keepdim=True)
    i_emb /= i_emb.norm(p=2, dim=-1, keepdim=True)
    
    return torch.matmul(t_emb, i_emb.T).item()

if __name__ == "__main__":
    try:
        l_txt = input("Enter lost description: ")
        f_txt = input("Enter found caption: ")
        l_img = input("Enter lost image path: ")
        f_img = input("Enter found image path: ")

        s1 = text_similarity(l_txt, f_txt)
        s2 = image_similarity(l_img, f_img)
        s3 = text_image_similarity(l_txt, f_img)

        final = (0.4 * s1) + (0.4 * s2) + (0.2 * s3)
        print(f"\nScores -> Text: {s1:.3f}, Image: {s2:.3f}, Cross: {s3:.3f}")
        print(f" Final Match Score: {final:.3f}")
        
    except Exception as e:
        print(f"Error: {e}")