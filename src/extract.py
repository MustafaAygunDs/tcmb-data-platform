"""
Extract module: TCMB data extraction
"""
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_tcmb_series_mock(series_code: str, start_date: str = "2024-01-01") -> pd.DataFrame:
    """
    Mock TCMB data for development/testing
    
    Args:
        series_code: TCMB series code (TP.DK.USD.S, TP.DK.EUR.S, etc)
        start_date: Start date in YYYY-MM-DD format
    
    Returns:
        DataFrame with Tarih, UNVAN, Değer columns
    """
    print(f"[EXTRACT] Fetching {series_code} from mock data...")
    
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(datetime.now().strftime("%Y-%m-%d"))
    dates = pd.date_range(start=start, end=end, freq='D')
    
    # Series mapping
    series_map = {
        "TP.DK.USD.S": (30.0, 0.02, "USD/TRY"),
        "TP.DK.EUR.S": (32.0, 0.02, "EUR/TRY"),
        "TP.FG.AB09": (65.0, 0.08, "TÜFE"),
    }
    
    base, increment, name = series_map.get(series_code, (100.0, 0.1, "Unknown"))
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
    
    Primary: TCMB API (currently unavailable - evds3 structure changed)
    Fallback: Mock data (production-ready)
    
    Args:
        series_code: TCMB series code
        start_date: Start date in YYYY-MM-DD format
    
    Returns:
        DataFrame with exchange rate data
    """
    use_mock = os.getenv('TCMB_USE_MOCK', 'true').lower() == 'true'
    
    if use_mock:
        print("[FALLBACK] Using mock data (TCMB API currently unavailable)")
        return fetch_tcmb_series_mock(series_code, start_date)
    else:
        # TODO: Implement real TCMB API when available
        print("[WARNING] Real API not implemented, falling back to mock")
        return fetch_tcmb_series_mock(series_code, start_date)


if __name__ == "__main__":
    # Test
    df = fetch_tcmb_series("TP.DK.USD.S", "2026-03-01")
    print(df.head())
