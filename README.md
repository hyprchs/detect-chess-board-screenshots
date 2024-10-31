# detect-chess-board-screenshots
Computer vision to detect/localize online/screenshotted chess boards. The final model is highly accurate!

<img src="https://github.com/user-attachments/assets/825308c0-9353-4b82-8c76-9ef4a9e68489" alt="Precision-recall curve" width="600"/>

## Synthetic dataset
I created a synthetic dataset of chess positions and fine-tuned a YOLOv8 model. The dataset contained 10,000 image + bounding box pairs produced by:
- finding and cleaning Lichess's SVG files for their different piece sets, which required learning more than I ever thought I would need to know about the SVG file format (thanks ChatGPT)
- modifying `python-chess`'s `svg.py` file to allow for rendering SVGs of boards with a specified piece set
- adapting `web-boardimage`:
  - to accept a `piece_set` param
  - to allow for a `color=random` param, which generates a random board color by producing a random light square color and calculating the dark squares with HSL color wheel math
- downloading games from [Lichess's game database](https://database.lichess.org/), then creating a list of 10k random FENs (while also recording the last move, and whether the side to move is in check)
  by selecting random plies from random games with equal probability
- downloading a small set of public-domain background images from Unsplash, making sure to get some images with physical chess boards and geometric patterns that could confuse the YOLO model
- generating 10k synthetic training images by:
  - choosing a random FEN / last move / check square
  - rendering the board as an SVG with the custom `web-boardimage` fork using either `Lichess`, `Chess.com`, `Wikipedia`, or `random` as the board color, and highlighting the last move and
    checking square as appropriate
  - choosing a random background image
  - choosing a random height/width for the board, which I chose to be at most `min(bg_height, bg_width)` and at least `min(bg_height, bg_width) / 4`
  - rasterizing the SVG and overlaying it on the background image in a random location, making note of the bounding box as a `(left, top, right, bottom)` tuple

## YOLOv8 fine-tuning results:
![image](https://github.com/user-attachments/assets/65d9e6fe-60ee-4724-8106-42d0dba38364)

## Some predictions on the validation set:
![image](https://github.com/user-attachments/assets/8c4f20d5-8817-4807-846a-99b5c434f4d9)
![image](https://github.com/user-attachments/assets/08b14f06-9f1b-448c-9d83-3fd22f4d7746)
