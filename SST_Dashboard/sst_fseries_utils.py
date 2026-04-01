# sst_fseries_utils.py
def normalize_leading_j0_row_if_needed(data_rows):
    """
    If the first data row has 3 floats but the next row has 6 floats,
    replace first row with 6 zeros.
    """
    if not data_rows:
        return data_rows
    if len(data_rows[0]) != 3:
        return data_rows
    nxt = None
    for k in range(1, len(data_rows)):
        if data_rows[k] and len(data_rows[k]) > 0:
            nxt = data_rows[k]
            break
    if nxt is not None and len(nxt) == 6:
        data_rows[0] = [0.0]*6
    return data_rows