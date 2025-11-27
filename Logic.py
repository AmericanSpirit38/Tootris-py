def check_full_rows(block_positions, rows, columns):
    """
    Given a list of block positions (as (x, y) tuples) and board dimensions,
    remove any fully occupied rows and shift blocks above those rows downward.

    Args:
        block_positions: list[tuple[int, int]] - current locked block positions.
        rows: int - total number of rows in the board.
        columns: int - total number of columns in the board.

    Returns:
        list[tuple[int, int]] - updated block positions after clearing and shifting.
    """
    if not block_positions:
        # Nothing to process
        return block_positions

    # Find full rows by counting how many blocks are in each row
    full_rows = []
    row_count = {row: 0 for row in range(rows)}
    for x, y in block_positions:
        row_count[y] += 1
    for row, count in row_count.items():
        if count == columns:
            full_rows.append(row)

    # Remove blocks that lie in any full row
    block_positions_new = []
    for pos in block_positions:
        if pos[1] not in full_rows:
            block_positions_new.append(pos)

    # Adjust remaining blocks downward by the number of cleared rows below them
    full_rows.sort()
    block_positions_adjusted = []
    for x, y in block_positions_new:
        # Count how many full rows are below this block (higher y index)
        rows_below = sum(1 for full_row in full_rows if full_row > y)
        block_positions_adjusted.append((x, y + rows_below))

    return block_positions_adjusted
