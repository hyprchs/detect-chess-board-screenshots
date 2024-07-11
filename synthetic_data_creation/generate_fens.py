import chess
from chess.pgn import read_game
import io
from time import perf_counter

# NOTE - Download and extract one of the `.pgn.zst` files at https://database.lichess.org/
input_pgn = 'lichess_db_standard_rated_2013-01.pgn'
output_file = 'fens.txt'

start_time = perf_counter()

with open(input_pgn, 'r') as f:
  strio = io.StringIO(f.read())

MAX_GAMES = 1_000
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

MAX_FENS = 1_000
fens = []

start_time = perf_counter()

while len(fens) < 10_000:
  if len(fens) % 1_000 == 0:
    print(f'Generated {len(fens)} FENs')
  
  game = random.choice(games)
  length = game.end().ply()
  ply = random.randint(0, length)
  node = game
  while node.ply() != ply:
    node = node.next()

  fens.append(node.board().fen())

with open(output_file, 'w') as f:
  f.write('\n'.join(fens))

print(f'Generated {len(fens)} FENs in {perf_counter() - start_time:.2f} seconds')
