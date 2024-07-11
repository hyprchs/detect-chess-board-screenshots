import os
from PIL import Image

# Directory path
images_dir = "background_images/"
output_dir = "resized_images/"

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Maximum dimension (width or height)
max_dimension = 800


# Function to resize images
def resize_image(image_path, output_path, max_dimension):
    with Image.open(image_path) as img:
        width, height = img.size
        if width > height:
            new_width = max_dimension
            new_height = int(new_width * height / width)
        else:
            new_height = max_dimension
            new_width = int(new_height * width / height)

        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        resized_img.save(output_path)


# Resize all images in the directory
for image_name in os.listdir(images_dir):
    image_path = os.path.join(images_dir, image_name)
    output_path = os.path.join(output_dir, image_name)
    resize_image(image_path, output_path, max_dimension)

print("Resizing complete.")
