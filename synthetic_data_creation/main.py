import os
import random
import requests
from PIL import Image
from io import BytesIO
from tqdm import tqdm
import json

# Directories and file paths
images_dir = "resized_images/"
fens_file_path = "fens.json"
output_dir = "output/"

NUM_TO_GENERATE = 1500


with open(fens_file_path, "r") as f:
    fens = json.load(f)

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)


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
def save_image_and_bounding_box(image, bounding_box, output_dir, image_name):
    output_image_path = os.path.join(output_dir, image_name)
    image.save(output_image_path)

    bounding_box_path = output_image_path.replace(".png", ".txt")
    with open(bounding_box_path, "w") as bbox_file:
        bbox_file.write(
            f"{bounding_box[0]},{bounding_box[1]},{bounding_box[2]},{bounding_box[3]}"
        )


# Main script logic
for i in tqdm(
    range(NUM_TO_GENERATE)
):  # Adjust the number of synthetic images you want to generate
    try:
        background_image_name = sample_image(images_dir)
        background_image_path = os.path.join(images_dir, background_image_name)
        background_image = Image.open(background_image_path).convert("RGBA")

        fenData = sample_fen()

        chessboard_image = generate_chessboard_image(fenData | {'colors': 'random'})

        overlayed_image, bounding_box = overlay_images(
            background_image, chessboard_image
        )

        output_image_name = f"synthetic_{i}.png"
        save_image_and_bounding_box(
            overlayed_image, bounding_box, output_dir, output_image_name
        )
    except Exception as e:
        print(f"Error generating synthetic image {i}: {e}")

print("Synthetic dataset generation complete.")
