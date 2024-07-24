import os
import random
import requests
from PIL import Image
from io import BytesIO
from tqdm import tqdm
import json
import argparse

# Directories and file paths
IMAGES_DIR = "resized_images/"
FENS_FILE_PATH = "fens.json"


# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--num", "-n", type=int, default=1000, help="Number of images to generate")
parser.add_argument("--image-output-dir", type=str, default="output/images", help="Output directory for images")
parser.add_argument("--bbox-output-dir", type=str, default="output/bounding_boxes", help="Output directory for bounding boxes")
args = parser.parse_args()

# Ensure the output directory exists
os.makedirs(args.image_output_dir, exist_ok=True)
os.makedirs(args.bbox_output_dir, exist_ok=True)

# Get the generated FENs
with open(FENS_FILE_PATH, "r") as f:
    fens = json.load(f)


# Function to randomly sample an image from the images directory
def sample_image(images_dir):
    return random.choice(os.listdir(images_dir))


# Function to randomly sample a FEN from the fens file
def sample_fen():
    return random.choice(fens)


# Function to generate a chessboard image from a FEN
def generate_chessboard_image(fenData):
    # First we need to url-encode the FEN
    response = requests.get(
        f"http://127.0.0.1:8080/board.png", params=fenData
    )
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        raise Exception("Failed to generate chessboard image")


# Function to overlay the chessboard image onto the background image
def overlay_images(background_image, chessboard_image):
    bg_width, bg_height = background_image.size
    min_size = min(bg_width, bg_height) // 4
    size = random.randint(min_size, min(bg_width, bg_height) - 1)
    chessboard_image = chessboard_image.resize((size, size))

    max_x = bg_width - size
    max_y = bg_height - size
    x = random.randint(0, max_x)
    y = random.randint(0, max_y)

    background_image.paste(chessboard_image, (x, y), chessboard_image.convert("RGBA"))

    return background_image, (x, y, x + size, y + size)


# Function to save the image and bounding box
def save_image_and_bounding_box(image, bounding_box, image_name):
    output_image_path = os.path.join(args.image_output_dir, image_name)
    bounding_box_path = os.path.join(
        args.bbox_output_dir, image_name.replace(".png", ".txt")
    )

    image.save(output_image_path)

    with open(bounding_box_path, "w") as bbox_file:
        bbox_file.write(
            f"{bounding_box[0]},{bounding_box[1]},{bounding_box[2]},{bounding_box[3]}"
        )


# Main script logic
for i in tqdm(range(args.num)):
    try:
        background_image_name = sample_image(IMAGES_DIR)
        background_image_path = os.path.join(IMAGES_DIR, background_image_name)
        background_image = Image.open(background_image_path).convert("RGBA")

        fenData = sample_fen()

        chessboard_image = generate_chessboard_image(fenData | {"colors": "random"})

        overlayed_image, bounding_box = overlay_images(
            background_image, chessboard_image
        )

        output_image_name = f"synthetic_{i}.png"
        save_image_and_bounding_box(overlayed_image, bounding_box, output_image_name)
    except Exception as e:
        print(f"Error generating synthetic image {i}: {e}")

print("Synthetic dataset generation complete.")
