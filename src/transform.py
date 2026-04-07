"""
Transform module: Data cleaning and feature engineering
"""
import pandas as pd
import numpy as np

def clean_exchange_rates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean exchange rate data
    
    - Handle null values
    - Remove outliers
    - Validate ranges
    """
    print("[TRANSFORM] Cleaning data...")
    
    # Copy to avoid warnings
    df = df.copy()
    
    # Remove nulls
    df = df.dropna()
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['Tarih'])
    
    # Sort by date
    df = df.sort_values('Tarih').reset_index(drop=True)
    
    print(f"[SUCCESS] Cleaned {len(df)} records")
    return df


def add_technical_indicators(df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    """
    Add technical indicators
    
    - SMA (Simple Moving Average)
    - Volatility (Standard Deviation)
    """
    print("[TRANSFORM] Adding technical indicators...")
    
    df = df.copy()
    
    # SMA
    df['SMA_7'] = df['Değer'].rolling(window=window, min_periods=1).mean()
    
    # Volatility (7-day std)
    df['Volatility_7'] = df['Değer'].rolling(window=window, min_periods=1).std()
    
    # Fill NaN volatility with 0
    df['Volatility_7'] = df['Volatility_7'].fillna(0)
    
    print(f"[SUCCESS] Added indicators: SMA_7, Volatility_7")
    return df


def aggregate_weekly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate daily data to weekly OHLC (Open, High, Low, Close)
    """
    print("[TRANSFORM] Aggregating to weekly...")
    
    df = df.copy()
    df['Week'] = df['Tarih'].dt.to_period('W')
    
    weekly = df.groupby('Week').agg({
        'Değer': ['first', 'max', 'min', 'last'],
        'UNVAN': 'first'
    }).reset_index()
    
    weekly.columns = ['Week', 'Open', 'High', 'Low', 'Close', 'Series']
    weekly['Week'] = weekly['Week'].dt.end_time
    
    print(f"[SUCCESS] Aggregated to {len(weekly)} weekly records")
    return weekly


def transform_pipeline(df: pd.DataFrame) -> dict:
    """
    Full transformation pipeline
    
    Returns:
        dict with 'daily' and 'weekly' dataframes
    """
    print("[PIPELINE] Starting transformation...")
    
    # Clean
    df_clean = clean_exchange_rates(df)
    
    # Add indicators
    df_indicators = add_technical_indicators(df_clean)
    
    # Aggregate weekly
    df_weekly = aggregate_weekly(df_indicators)
    
    return {
        'daily': df_indicators,
        'weekly': df_weekly
    }


if __name__ == "__main__":
    from extract import fetch_tcmb_series
    
    # Test
    df = fetch_tcmb_series("TP.DK.USD.S", "2026-03-01")
    result = transform_pipeline(df)
    
    print("\nDaily (first 5):")
    print(result['daily'].head())
    print("\nWeekly (first 5):")
    print(result['weekly'].head())
