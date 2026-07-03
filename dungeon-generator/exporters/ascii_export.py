def render(dungeon):
    return "\n".join("".join(row) for row in dungeon.grid)
