import chess
from chess.pgn import read_game
import io
from time import perf_counter

# NOTE - Download and extract one of the `.pgn.zst` files at https://database.lichess.org/
input_pgn = 'lichess_db_standard_rated_2013-01.pgn'
output_file = 'fens.json'

start_time = perf_counter()

with open(input_pgn, 'r') as f:
  strio = io.StringIO(f.read())

MAX_GAMES = 5_000
games = []
games_read = 0
while True:
  g = read_game(strio)
  if g is None:
    break

  games.append(g)
  games_read += 1

  if games_read % 1_000 == 0:
    print(f'Read {games_read} games')

  if games_read == MAX_GAMES:
    break

print(f'Read {len(games)} games in {perf_counter() - start_time:.2f} seconds')

# Until we get 10_000 FENs, do the following:
#  - Get a random game from `games`
#  - Get a random position from the game:
#    - Get the length of the game with `game.end().ply()`
#    - Get a random ply number with `random.randint(0, length)`
#    - Loop through `node`s the `game.mainline()` until `node.ply() == ply`
#    - Get the FEN of the position with `node.board().fen()`
#  - Write the FEN to the `fens_file_path`

import random
import json

MAX_FENS = 10_000
fenData = []

start_time = perf_counter()

while len(fenData) < MAX_FENS:
    # Get random game
    game = random.choice(games)

    # Get random position with equal probability across plies
    length = game.end().ply()
    ply = random.randint(0, length)
    node = game
    while node.ply() != ply:
        node = node.next()

    # Add data about this position
    nextFen = {
      "fen": node.board().fen(),
    }

    # Get the last move if we're not in the root node
    if node.move is not None:
        nextFen['lastMove'] = node.move.uci()

    # Get the check square if the position is in check
    b = node.board()
    if b.is_check():
        nextFen['check'] = chess.square_name(next(iter(chess.SquareSet(b.kings & b.occupied_co[b.turn]))))

    fenData.append(nextFen)

    if len(fenData) % 1_000 == 0:
        print(f'Generated {len(fenData)} FENs')

with open(output_file, 'w') as f:
  json.dump(fenData, f)

print(f'Generated {len(fenData)} FENs in {perf_counter() - start_time:.2f} seconds')
