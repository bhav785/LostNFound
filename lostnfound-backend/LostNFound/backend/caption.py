from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# -----------------------------
# Load BLIP Model (CPU)
# -----------------------------
print("Loading BLIP model... Please wait.")

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

print("Model loaded successfully.\n")

# -----------------------------
# Function to Generate Caption
# -----------------------------
def generate_caption(image_path):
    image = Image.open(image_path).convert("RGB")

    inputs = processor(image, return_tensors="pt")
    output = model.generate(**inputs)

    caption = processor.decode(output[0], skip_special_tokens=True)

    return caption


# -----------------------------
# Run Program
# -----------------------------
if __name__ == "__main__":
    image_path = input("Enter path of found image: ")

    print("\nGenerating description...")
    caption = generate_caption(image_path)

    print("\n📝 Generated Description:")
    print(caption)