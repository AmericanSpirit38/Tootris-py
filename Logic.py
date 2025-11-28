def check_full_rows(block_positions, rows, columns):
    """
    Return (updated_block_positions, lines_cleared).
    """
    if not block_positions:
        return block_positions, 0

    # Find full rows
    full_rows = []
    row_count = {row: 0 for row in range(rows)}
    for x, y in block_positions:
        row_count[y] += 1
    for row, count in row_count.items():
        if count == columns:
            full_rows.append(row)

    # Remove blocks in full rows
    block_positions_new = [pos for pos in block_positions if pos[1] not in full_rows]

    # Shift remaining blocks down by number of cleared rows below them
    full_rows.sort()
    block_positions_adjusted = []
    for x, y in block_positions_new:
        rows_below = sum(1 for full_row in full_rows if full_row > y)
        block_positions_adjusted.append((x, y + rows_below))

    return block_positions_adjusted, len(full_rows)


def SetScore(lines_cleared):
    """
    Return the score delta for the given number of cleared lines.
    """
    scoring = {1: 100, 2: 300, 3: 600, 4: 1000}
    return scoring.get(lines_cleared, 0)
