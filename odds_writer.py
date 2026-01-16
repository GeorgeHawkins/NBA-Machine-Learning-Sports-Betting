import gspread
from dotenv import load_dotenv
import os
from main import get_structured_games
import json

load_dotenv()

def _column_number_to_letter(col_num):
    """Convert column number (1-based) to column letter (A, B, C, ..., Z)."""
    return chr(64 + col_num)

# ANSI color codes for terminal output
GREEN = '\033[92m'  # Green for increases
RED = '\033[91m'    # Red for decreases
RESET = '\033[0m'   # Reset to default color

def normalize_value(val):
    """Normalize value for comparison - handle percentages, strings, numbers"""
    if val == "" or val is None:
        return None
    val_str = str(val).strip()
    # Remove percentage sign and convert
    if '%' in val_str:
        try:
            return float(val_str.replace('%', '').replace(',', '')) / 100.0
        except ValueError:
            return val_str
    # Try to convert to float
    try:
        return float(val_str.replace(',', ''))
    except ValueError:
        return val_str

def print_row_comparison(row_index, existing_row, new_values, header_row, game_name=None):
    """Print a formatted comparison of old vs new values for a row update."""
    print(f"\n{'='*80}")
    if game_name:
        print(f"Updating: {game_name}")
    else:
        print(f"Updating Row {row_index}")
    print(f"{'='*80}")
    
    # Find which columns changed
    changed_cols = []
    max_cols = max(len(existing_row), len(new_values))
    
    for col_idx in range(max_cols):
        old_val = existing_row[col_idx] if col_idx < len(existing_row) else ""
        new_val = new_values[col_idx] if col_idx < len(new_values) else ""
        
        old_norm = normalize_value(old_val)
        new_norm = normalize_value(new_val)
        
        # Compare normalized values
        if isinstance(old_norm, float) and isinstance(new_norm, float):
            if abs(old_norm - new_norm) > 0.0001:  # Small tolerance for floating point
                changed_cols.append(col_idx)
        elif old_norm != new_norm:
            changed_cols.append(col_idx)
    
    # Display comparison - show all columns or just changed ones
    if changed_cols:
        print(f"\nChanged columns ({len(changed_cols)} of {max_cols}):")
        print(f"{'-'*80}")
        print(f"{'Col':<4} {'Column Name':<25} {'OLD VALUE':<25} {'NEW VALUE':<25}")
        print(f"{'-'*80}")
        
        for col_idx in changed_cols:
            col_name = header_row[col_idx] if col_idx < len(header_row) else f"Col {col_idx + 1}"
            old_val = existing_row[col_idx] if col_idx < len(existing_row) else ""
            new_val = new_values[col_idx] if col_idx < len(new_values) else ""
            
            # Determine if value went up or down (for numeric values)
            old_norm = normalize_value(old_val)
            new_norm = normalize_value(new_val)
            
            # Format new value with color
            new_val_plain = str(new_val)[:24]
            new_val_str = new_val_plain
            if isinstance(old_norm, float) and isinstance(new_norm, float):
                if new_norm > old_norm:
                    new_val_str = f"{GREEN}{new_val_plain}{RESET}"
                elif new_norm < old_norm:
                    new_val_str = f"{RED}{new_val_plain}{RESET}"
            
            # Calculate padding needed (ANSI codes don't count toward display width)
            padding_needed = max(0, 25 - len(new_val_plain))
            new_val_display = f"{new_val_str}{' ' * padding_needed}"
            
            print(f"{col_idx+1:<4} {col_name[:24]:<25} {str(old_val)[:24]:<25} {new_val_display}")
    else:
        print("No changes detected (values are identical)")

def format_game_data(worksheet, games):
    existing_data = worksheet.get_all_values()
    
    # Find column indices from header row
    date_col_idx = None
    home_team_col_idx = None
    away_team_col_idx = None
    
    if len(existing_data) > 0:
        header_row = existing_data[0]
        for idx, header_cell in enumerate(header_row):
            header_cell_lower = header_cell.strip().lower()
            if date_col_idx is None and 'date' in header_cell_lower:
                date_col_idx = idx
            elif home_team_col_idx is None and ('home team' in header_cell_lower):
                home_team_col_idx = idx
            elif away_team_col_idx is None and ('away team' in header_cell_lower):
                away_team_col_idx = idx
    
    # Fallback to hardcoded indices if headers not found
    if date_col_idx is None:
        date_col_idx = 0
    if home_team_col_idx is None:
        home_team_col_idx = 1
    if away_team_col_idx is None:
        away_team_col_idx = 6
    
    # Create a mapping of (date, home_team, away_team) -> row_index (1-indexed)
    # Assuming headers in row 1, data starts at row 2
    existing_rows_map = {}
    if len(existing_data) > 1:  # Has header and at least one data row
        for idx, row in enumerate(existing_data[1:], start=2):  # Start at row 2 (skip header)
            max_col_needed = max(date_col_idx, home_team_col_idx, away_team_col_idx)
            if len(row) > max_col_needed:
                date = row[date_col_idx] if len(row) > date_col_idx else ""
                home_team = row[home_team_col_idx] if len(row) > home_team_col_idx else ""
                away_team = row[away_team_col_idx] if len(row) > away_team_col_idx else ""
                key = (date, home_team, away_team)
                if all(key):  # Only add if all three values are non-empty
                    existing_rows_map[key] = idx
    
    rows_to_update = []
    rows_to_append = []
    
    for game in games:
        max_col_needed = max(date_col_idx, home_team_col_idx, away_team_col_idx)
        if len(game) <= max_col_needed:
            continue
        
        date = str(game[date_col_idx])
        home_team = str(game[home_team_col_idx])
        away_team = str(game[away_team_col_idx])
        key = (date, home_team, away_team)
        
        if key in existing_rows_map:
            rows_to_update.append((existing_rows_map[key], game))
        else:
            rows_to_append.append(game)
    return rows_to_update, rows_to_append


def write_game_data(games):
    gc = gspread.service_account(filename='service-account.json')
    sheet = gc.open_by_key(os.getenv('GOOGLE_SHEETS_KEY'))
    all_games_worksheet = sheet.worksheet('All Games')

    rows_to_update, rows_to_append = format_game_data(all_games_worksheet, games)
    # Perform batch updates
    if rows_to_update:
        # Get header row for column names
        existing_data = all_games_worksheet.get_all_values()
        header_row = existing_data[0] if len(existing_data) > 0 else []
        
        # Find column indices for home team and away team
        home_team_col_idx = None
        away_team_col_idx = None
        for idx, header_cell in enumerate(header_row):
            header_cell_lower = header_cell.strip().lower()
            if home_team_col_idx is None and ('home team' in header_cell_lower):
                home_team_col_idx = idx
            elif away_team_col_idx is None and ('away team' in header_cell_lower):
                away_team_col_idx = idx
        
        # Fallback to hardcoded indices if headers not found (B=1, G=6)
        if home_team_col_idx is None:
            home_team_col_idx = 1
        if away_team_col_idx is None:
            away_team_col_idx = 6
        
        # gspread's batch_update requires ranges and values
        # We'll update rows individually or in batches
        # For efficiency, we can batch multiple updates in one call
        update_data = []
        for row_index, new_values in rows_to_update:
            # Get existing row data to show what's changing
            existing_row = all_games_worksheet.row_values(row_index)
            # Pad existing_row to match new_values length if needed
            while len(existing_row) < len(new_values):
                existing_row.append("")
            
            # Extract home team and away team names for display
            home_team = existing_row[home_team_col_idx] if home_team_col_idx < len(existing_row) else ""
            away_team = existing_row[away_team_col_idx] if away_team_col_idx < len(existing_row) else ""
            game_name = f"{home_team} vs {away_team}" if home_team and away_team else None
            
            # Print comparison of old vs new values
            print_row_comparison(row_index, existing_row, new_values, header_row, game_name)
            
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

games = get_structured_games(sportsbook="sportsbet")

write_game_data(games)