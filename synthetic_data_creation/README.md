# Synthetic data creation for chess board screenshots with bounding boxes

This script generates images of chess board screenshots overlayed on stock images, along with a bounding box annotation
over the image. The boards are randomly scaled (within certain height/width requirements) and are generated with random
square colors. FEN positions come from the Lichess database of standard rated games played in 2013-01.

## Usage

1. Generate `fens.json`:
    
    a. Download one of the Lichess PGN exports from https://database.lichess.org/. A relatively small PGN file can generate a large amount of random FENs. I chose the very first export from [`2013-01`](https://database.lichess.org/standard/lichess_db_standard_rated_2013-01.pgn.zst). Extract it so it's just a `.pgn` file.
    
    b. Run:
    ```sh
    python generate_fens.py --input-pgn path/to/extracted.pgn
    ```

1. Run `main.sh` to automatically launch the `web-boardimage` server, which is used to generate PGNs from FENs, and then run `main.py` to generate and save annotated images. Optionally choose how many to generate (defaults to 1000) or specify different output dirs. The format of the generated bounding boxes is `(x_min, y_min, x_max, y_max)`. Metadata about each image is also saved to the specified directory, such as the FEN, orientation, piece set, and highlighted last move in the image's board.

```sh
./main.sh [-n 1000] [--image-output-dir output/images] [--bbox-output-dir output/bounding_boxes] [--metadata-output-dir output/metadata]
```
