import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from datetime import datetime

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found. Please add it to your .env file")

# ----------------------------
# Initialize HuggingFace Client
# ----------------------------
client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN,
)

# ----------------------------
# Function to Generate Image
# ----------------------------
def generate_lost_item_image(description: str):
    try:
        prompt = f"""
        Realistic product photo of:
        {description}.
        White background, high resolution, detailed, natural lighting.
        """

        print("\nGenerating image... Please wait...")

        image = client.text_to_image(
            prompt,
            model="stabilityai/stable-diffusion-xl-base-1.0",
        )

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        IMAGE_DIR = os.path.join(BASE_DIR, "generated_images")

        os.makedirs(IMAGE_DIR, exist_ok=True)

        filename = os.path.join(
            IMAGE_DIR,
            f"lost_item_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )


        # Save image locally
        image.save(filename)

        print(f"\n✅ Image saved successfully at: {filename}")
        return filename

    except Exception as e:
        print("\n❌ Error occurred:")
        print(e)


# ----------------------------
# Run Program
# ----------------------------
if __name__ == "__main__":
    user_description = input("Enter lost item description: ")
    generate_lost_item_image(user_description)