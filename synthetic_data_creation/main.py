import os
import random
import shutil
from typing import Any, Literal, TypedDict
import requests
import cv2
import numpy as np
from io import BytesIO
from tqdm import tqdm
import json
import argparse
import chess

# Directories and file paths
BACKGROUND_IMAGES_DIR = "resized_images/"
FENS_FILE_PATH = "fen_data_list.json"
PIECE_SETS = [
    "alpha",
    "anarcandy",
    "caliente",
    "california",
    "cardinal",
    "cburnett",
    "celtic",
    "chess7",
    "chessnut",
    "companion",
    "cooke",
    "dubrovny",
    "fantasy",
    "fresca",
    "gioco",
    "governor",
    "horsey",
    "icpieces",
    "kiwen-suwi",
    "kosal",
    "leipzig",
    "letter",
    "libra",
    "maestro",
    "merida",
    "monarchy",
    "mpchess",
    "pirouetti",
    "pixel",
    "reillycraig",
    "riohacha",
    "shapes",
    "spatial",
    "staunty",
    "tatiana",
]

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "--num", "-n", type=int, default=1000, help="Number of images to generate"
)
parser.add_argument(
    "--image-output-dir",
    type=str,
    default="output/images",
    help="Output directory for images",
)
parser.add_argument(
    "--bbox-output-dir",
    type=str,
    default="output/bounding_boxes",
    help="Output directory for bounding boxes",
)
parser.add_argument(
    "--metadata-output-dir",
    type=str,
    default="output/metadata",
    help="Output directory with metadata about the generated images, such as the FEN, highlighted last move, orientation, etc.",
)
args = parser.parse_args()

# Delete and recreate output directories
shutil.rmtree(args.image_output_dir)
shutil.rmtree(args.bbox_output_dir)
shutil.rmtree(args.metadata_output_dir)
os.makedirs(args.image_output_dir, exist_ok=True)
os.makedirs(args.bbox_output_dir, exist_ok=True)
os.makedirs(args.metadata_output_dir, exist_ok=True)


class FenData(TypedDict):
    fen: str
    lastMove: str


class WebBoardimageParams(TypedDict):
    fen: str
    """FEN of the position with at least the board part"""

    orientation: Literal["white", "black"] = "white"
    """`white` or `black`"""

    size: int | None  # Note: API defaults this to 360, but we choose a random size, so leave as `None`
    """The width and height of the image"""

    lastMove: str | None
    """The last move to highlight, e.g., `f4g6`"""

    check: str | None
    """A square to highlight for check"""

    arrows: str | None
    """Draw arrows and circles, e.g., `Ge6g8,Bh7`, possible color prefixes: `G`, `B`, `R`, `Y`"""

    squares: str | None
    """Marked squares, e.g., `a3,c3`"""

    coordinates: bool = False
    """Show a coordinate margin"""

    colors: Literal["wikipedia", "lichess-brown", "lichess-blue", "random"] = (
        "lichess-brown"
    )
    """Theme: `wikipedia`, `lichess-brown`, `lichess-blue`, `random` (generate one on the fly)"""

    piece_set: Literal[
        "alpha",
        "anarcandy",
        "caliente",
        "california",
        "cardinal",
        "cburnett",
        "celtic",
        "chess7",
        "chessnut",
        "companion",
        "cooke",
        "dubrovny",
        "fantasy",
        "fresca",
        "gioco",
        "governor",
        "horsey",
        "icpieces",
        "kiwen-suwi",
        "kosal",
        "leipzig",
        "letter",
        "libra",
        "maestro",
        "merida",
        "monarchy",
        "mpchess",
        "pirouetti",
        "pixel",
        "reillycraig",
        "riohacha",
        "shapes",
        "spatial",
        "staunty",
        "tatiana",
    ]


# Load the FEN data
with open(FENS_FILE_PATH, "r") as f:
    fen_data_list: list[FenData] = json.load(f)


def sample_background_image_file() -> str:
    """Return a random background image file from the `BACKGROUND_IMAGES_DIR` directory."""
    return random.choice(os.listdir(BACKGROUND_IMAGES_DIR))


def sample_fen() -> FenData:
    """Return a random FEN from the `fens` list."""
    return random.choice(fen_data_list)


def generate_chessboard_image(params: dict[str, Any]) -> np.ndarray:
    """Generate a chessboard image using the FEN data."""
    response = requests.get(f"http://127.0.0.1:8080/board.png", params=params)
    if response.status_code == 200:
        chessboard_image = np.asarray(bytearray(response.content), dtype="uint8")
        chessboard_image = cv2.imdecode(chessboard_image, cv2.IMREAD_UNCHANGED)
        return chessboard_image
    else:
        raise Exception("Failed to generate chessboard image")


def get_square_bounding_boxes(board_bbox: tuple[int, int, int, int], orientation: Literal['white', 'black']) -> dict[chess.Square, tuple[float, float, float, float]]:
    """
    Return the bounding boxes of each square on the chessboard given the bounding box of the entire board.
    """
    x_min, y_min, x_max, y_max = board_bbox
    square_width = (x_max - x_min) / 8
    square_height = (y_max - y_min) / 8

    square_bounding_boxes = {}
    for square in chess.SQUARES:
        if orientation == 'white':
            rank_from_top = 7 - chess.square_rank(square)
            file_from_left = chess.square_file(square)
        else:
            rank_from_top = chess.square_rank(square)
            file_from_left = 7 - chess.square_file(square)

        x1 = x_min + file_from_left * square_width
        y1 = y_min + rank_from_top * square_height
        x2 = x1 + square_width
        y2 = y1 + square_height
        square_bounding_boxes[square] = (x1, y1, x2, y2)
    
    return square_bounding_boxes


def overlay_images(
    background_image: np.ndarray, chessboard_image: np.ndarray
) -> tuple[np.ndarray, tuple[int, int, int, int]]:
    """
    Overlay the chessboard image on the background image, and return the final image, the
    bounding box of the chessboard, and the mapping of squares to their bounding boxes.
    The bounding box format is `(x_min, y_min, x_max, y_max)`.
    """
    bg_height, bg_width, _ = background_image.shape
    min_size = min(bg_width, bg_height) // 4
    size = random.randint(min_size, min(bg_width, bg_height) - 1)
    chessboard_image = cv2.resize(
        chessboard_image, (size, size), interpolation=cv2.INTER_AREA
    )

    max_x = bg_width - size
    max_y = bg_height - size
    x = random.randint(0, max_x)
    y = random.randint(0, max_y)

    # Ensure both images have the same number of channels
    if background_image.shape[2] == 3:
        background_image = cv2.cvtColor(background_image, cv2.COLOR_BGR2BGRA)
    if chessboard_image.shape[2] == 3:
        chessboard_image = cv2.cvtColor(chessboard_image, cv2.COLOR_BGR2BGRA)

    # Overlay the images
    overlay = background_image.copy()
    alpha_s = chessboard_image[:, :, 3] / 255.0
    alpha_l = 1.0 - alpha_s

    for c in range(0, 3):
        overlay[y : y + size, x : x + size, c] = (
            alpha_s * chessboard_image[:, :, c]
            + alpha_l * overlay[y : y + size, x : x + size, c]
        )

    return overlay, (x, y, x + size, y + size)


def save_image_and_annotation_info(
    image: np.ndarray,
    bounding_box: tuple[int, int, int, int],
    metadata: dict[str, str],
    image_name: str,
) -> None:
    # Save image
    output_image_filepath = os.path.join(args.image_output_dir, image_name)
    cv2.imwrite(output_image_filepath, image)

    # Save bounding box
    bounding_box_filepath = os.path.join(
        args.bbox_output_dir, image_name.replace(".png", ".txt")
    )
    with open(bounding_box_filepath, "w") as f:
        f.write(
            f"{bounding_box[0]},{bounding_box[1]},{bounding_box[2]},{bounding_box[3]}"
        )

    # Save metadata
    metadata_filepath = os.path.join(
        args.metadata_output_dir, image_name.replace(".png", ".txt")
    )
    with open(metadata_filepath, "w") as f:
        json.dump(metadata, f)


# Main script logic
for i in tqdm(range(args.num)):
    background_image_name = sample_background_image_file()
    background_image_path = os.path.join(
        BACKGROUND_IMAGES_DIR, background_image_name
    )
    background_image = cv2.imread(background_image_path, cv2.IMREAD_UNCHANGED)

    fenData = sample_fen()
    
    orientation = random.choice((chess.WHITE, chess.BLACK))

    web_boardimage_params = WebBoardimageParams(
        fen=fenData["fen"],
        lastMove=fenData.get("lastMove", None),
        colors=random.choice(("wikipedia", "lichess-brown", "lichess-blue", "random")),
        orientation=orientation,
        pieceSet=random.choice(PIECE_SETS),
        size=1000,
    )

    chessboard_image = generate_chessboard_image(web_boardimage_params)

    overlayed_image, board_bbox = overlay_images(
        background_image, chessboard_image
    )

    square_bboxes = get_square_bounding_boxes(board_bbox, orientation)

    output_image_name = f"{i:>06}.png"
    save_image_and_annotation_info(
        overlayed_image, board_bbox, web_boardimage_params, output_image_name
    )

print("Synthetic dataset generation complete.")
