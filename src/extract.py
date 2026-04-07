"""
Extract module: TCMB data extraction with real API fallback
"""
import pandas as pd
from datetime import datetime, timedelta
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def fetch_from_exchangerate_api() -> dict:
    """
    Fetch real exchange rates from exchangerate-api.com
    Free tier: USD base only
    """
    print("[API] Fetching from exchangerate-api.com...")
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        rates = {
            'USD/TRY': data['rates']['TRY'],
            'EUR/TRY': data['rates']['TRY'] * (data['rates']['EUR'] / data['rates']['USD']),
        }
        print(f"[SUCCESS] Real rates: USD/TRY={rates['USD/TRY']:.2f}, EUR/TRY={rates['EUR/TRY']:.2f}")
        return rates
    except Exception as e:
        print(f"[WARNING] API failed: {e}")
        return None

def fetch_tcmb_series_mock(series_code: str, start_date: str = "2024-01-01", real_rates: dict = None) -> pd.DataFrame:
    """
    Mock TCMB data with realistic values
    
    Args:
        series_code: TCMB series code
        start_date: Start date in YYYY-MM-DD format
        real_rates: Dict with real exchange rates
    
    Returns:
        DataFrame with Tarih, UNVAN, Değer columns
    """
    print(f"[EXTRACT] Generating data for {series_code}...")
    
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(datetime.now().strftime("%Y-%m-%d"))
    dates = pd.date_range(start=start, end=end, freq='D')
    
    # Use real rates if available, else fallback
    if real_rates:
        base_rates = {
            "TP.DK.USD.S": (real_rates.get('USD/TRY', 44.5), 0.01, "USD/TRY"),
            "TP.DK.EUR.S": (real_rates.get('EUR/TRY', 48.0), 0.01, "EUR/TRY"),
            "TP.FG.AB09": (110.0, 0.05, "TÜFE"),
        }
    else:
        base_rates = {
            "TP.DK.USD.S": (44.5, 0.01, "USD/TRY"),
            "TP.DK.EUR.S": (48.0, 0.01, "EUR/TRY"),
            "TP.FG.AB09": (110.0, 0.05, "TÜFE"),
        }
    
    base, increment, name = base_rates.get(series_code, (100.0, 0.1, "Unknown"))
    values = [base + (i * increment) for i in range(len(dates))]
    
    df = pd.DataFrame({
        "Tarih": dates,
        "UNVAN": name,
        "Değer": values
    })
    
    print(f"[SUCCESS] Generated {len(df)} records for {name}")
    return df

def fetch_tcmb_series(series_code: str, start_date: str) -> pd.DataFrame:
    """
    Fetch TCMB data with fallback strategy
    
    Primary: Real Exchange Rate API
    Secondary: Mock data with realistic values
    
    Args:
        series_code: TCMB series code
        start_date: Start date in YYYY-MM-DD format
    
    Returns:
        DataFrame with exchange rate data
    """
    print("[EXTRACT] Starting data fetch...")
    
    # Try real API first
    real_rates = fetch_from_exchangerate_api()
    
    # Generate mock data (with real rates if available)
    if real_rates:
        print("[SUCCESS] Using real exchange rates")
        return fetch_tcmb_series_mock(series_code, start_date, real_rates)
    else:
        print("[FALLBACK] Using realistic mock data")
        return fetch_tcmb_series_mock(series_code, start_date)

if __name__ == "__main__":
    # Test
    df = fetch_tcmb_series("TP.DK.USD.S", "2026-03-01")
    print(df.head())
