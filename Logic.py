def check_full_rows(block_positions, rows, columns):
    if not block_positions:
        return block_positions

    # Find full rows
    full_rows = []
    row_count = {row: 0 for row in range(rows)}
    for x, y in block_positions:
        row_count[y] += 1
    for row, count in row_count.items():
        if count == columns:
            full_rows.append(row)

    # Remove blocks in full rows
    block_positions_new = []
    for pos in block_positions:
        if pos[1] not in full_rows:
            block_positions_new.append(pos)

    # Adjust remaining blocks downward
    full_rows.sort()
    block_positions_adjusted = []
    for x, y in block_positions_new:
        # Count how many full rows are below this block
        rows_below = sum(1 for full_row in full_rows if full_row > y)
        block_positions_adjusted.append((x, y + rows_below))

    return block_positions_adjusted
