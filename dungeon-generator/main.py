import argparse
from dungeon import Dungeon
from ascii import render

parser = argparse.ArgumentParser(description="Procedural Dungeon Generator")
parser.add_argument("--width",     type=int, default=64)
parser.add_argument("--height",    type=int, default=40)
parser.add_argument("--depth",     type=int, default=5)
parser.add_argument("--seed",      type=int, default=None)
args = parser.parse_args()

dungeon = Dungeon(
    width=args.width,
    height=args.height,
    max_depth=args.depth,
    seed=args.seed
).generate()

print(render(dungeon))
print(f"\n{len(dungeon.rooms)} rooms, {len(dungeon.corridors)} corridors")