"""
Utils module: Helper functions
"""
import pandas as pd
import json
import os
from datetime import datetime

def save_to_csv(df: pd.DataFrame, filename: str, directory: str = "data"):
    """Save dataframe to CSV"""
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, f"{filename}.csv")
    df.to_csv(filepath, index=False)
    print(f"[SAVE] Saved to {filepath}")

def save_to_json(df: pd.DataFrame, filename: str, directory: str = "data"):
    """Save dataframe to JSON"""
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, f"{filename}.json")
    df.to_json(filepath, orient='records', date_format='iso')
    print(f"[SAVE] Saved to {filepath}")

def log_execution(stage: str, status: str, details: str = ""):
    """Log execution details"""
    timestamp = datetime.now().isoformat()
    message = f"[{timestamp}] {stage}: {status}"
    if details:
        message += f" - {details}"
    print(message)

def format_dataframe(df: pd.DataFrame) -> str:
    """Format dataframe for display"""
    return df.to_string()

if __name__ == "__main__":
    print("[UTILS] Helper functions loaded")
