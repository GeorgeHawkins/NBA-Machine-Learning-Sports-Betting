import gspread
from dotenv import load_dotenv
import os
from main import get_structured_games

load_dotenv()

def _column_number_to_letter(col_num):
    """Convert column number (1-based) to column letter (A, B, C, ..., Z)."""
    return chr(64 + col_num)

def format_game_data(worksheet, games):
    existing_data = worksheet.get_all_values()
    
    # Create a mapping of (date, home_team, away_team) -> row_index (1-indexed)
    # Assuming headers in row 1, data starts at row 2
    existing_rows_map = {}
    if len(existing_data) > 1:  # Has header and at least one data row
        for idx, row in enumerate(existing_data[1:], start=2):  # Start at row 2 (skip header)
            if len(row) >= 6:  # Ensure we have at least date, home_team, and away_team columns
                date = row[0] if len(row) > 0 else ""
                home_team = row[1] if len(row) > 1 else ""
                away_team = row[5] if len(row) > 5 else ""
                key = (date, home_team, away_team)
                if all(key):  # Only add if all three values are non-empty
                    existing_rows_map[key] = idx
    
    rows_to_update = []
    rows_to_append = []
    
    for game in games:
        if len(game) < 6:
            continue
        
        date = str(game[0])
        home_team = str(game[1])
        away_team = str(game[5])
        key = (date, home_team, away_team)
        
        if key in existing_rows_map:
            rows_to_update.append((existing_rows_map[key], game))
        else:
            rows_to_append.append(game)
    return rows_to_update, rows_to_append


def write_game_data(games):
    gc = gspread.service_account(filename='service-account.json')
    sheet = gc.open_by_key(os.getenv('GOOGLE_SHEETS_KEY'))
    all_games_worksheet = sheet.worksheet('All Games - Working')

    rows_to_update, rows_to_append = format_game_data(all_games_worksheet, games)
    # Perform batch updates
    if rows_to_update:
        # gspread's batch_update requires ranges and values
        # We'll update rows individually or in batches
        # For efficiency, we can batch multiple updates in one call
        update_data = []
        for row_index, new_values in rows_to_update:
            # Calculate the range (e.g., "A2:L2" for row 2 with 12 columns)
            num_cols = len(new_values)
            end_col = _column_number_to_letter(num_cols)
            range_name = f"A{row_index}:{end_col}{row_index}"
            update_data.append({
                'range': range_name,
                'values': [new_values]
            })
        
        if update_data:
            all_games_worksheet.batch_update(update_data)
    
    if rows_to_append:
        # Find the last row with data in column A (to avoid append_rows finding stray data in other columns)
        column_a_values = all_games_worksheet.col_values(1)  # Column A is index 1
        # col_values returns values from row 1 onwards, so length tells us the last row with data
        # Next row to append to is len(column_a_values) + 1
        start_row = len(column_a_values) + 1
        num_cols = len(rows_to_append[0]) if rows_to_append else 0
        end_col = _column_number_to_letter(num_cols)
        
        # Use update with calculated range instead of append_rows
        range_name = f"A{start_row}:{end_col}{start_row + len(rows_to_append) - 1}"
        all_games_worksheet.update(rows_to_append, range_name)

games = get_structured_games()

write_game_data(games)