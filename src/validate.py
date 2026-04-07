"""
Validate module: Data quality checks
"""
import pandas as pd
from datetime import datetime

def validate_null_dates(df: pd.DataFrame) -> tuple[bool, str]:
    """Check for null dates"""
    null_count = df['Tarih'].isnull().sum()
    if null_count > 0:
        return False, f"Found {null_count} null dates"
    return True, "No null dates ✅"

def validate_null_values(df: pd.DataFrame) -> tuple[bool, str]:
    """Check for null values"""
    null_count = df['Değer'].isnull().sum()
    if null_count > 0:
        return False, f"Found {null_count} null values"
    return True, "No null values ✅"

def validate_value_range(df: pd.DataFrame, min_val: float = 1, max_val: float = 150) -> tuple[bool, str]:
    """Check value range"""
    invalid = df[(df['Değer'] < min_val) | (df['Değer'] > max_val)]
    if len(invalid) > 0:
        return False, f"Found {len(invalid)} out-of-range values"
    return True, f"All values in range ({min_val}-{max_val}) ✅"

def validate_sequential_dates(df: pd.DataFrame) -> tuple[bool, str]:
    """Check for sequential dates"""
    df_sorted = df.sort_values('Tarih')
    date_diffs = df_sorted['Tarih'].diff()
    non_sequential = (date_diffs != pd.Timedelta(days=1)).sum()
    if non_sequential > 1:
        return False, f"Found {non_sequential} non-sequential dates"
    return True, "Dates are sequential ✅"

def validate_duplicates(df: pd.DataFrame) -> tuple[bool, str]:
    """Check for duplicates"""
    dup_count = df.duplicated(subset=['Tarih']).sum()
    if dup_count > 0:
        return False, f"Found {dup_count} duplicate dates"
    return True, "No duplicates ✅"

def run_validation(df: pd.DataFrame) -> dict:
    """Run all quality checks"""
    print("[VALIDATE] Running data quality checks...")
    
    checks = {
        'null_dates': validate_null_dates(df),
        'null_values': validate_null_values(df),
        'value_range': validate_value_range(df),
        'sequential_dates': validate_sequential_dates(df),
        'duplicates': validate_duplicates(df),
    }
    
    # Summary
    passed = sum(1 for status, _ in checks.values() if status)
    total = len(checks)
    score = (passed / total) * 100
    
    print("\n" + "="*50)
    print(f"DATA QUALITY REPORT")
    print("="*50)
    for check_name, (status, message) in checks.items():
        print(f"{check_name:20} {message}")
    print("="*50)
    print(f"Quality Score: {score:.1f}% ({passed}/{total})")
    print("="*50 + "\n")
    
    return {
        'checks': checks,
        'passed': passed,
        'total': total,
        'score': score,
        'timestamp': datetime.now().isoformat()
    }

if __name__ == "__main__":
    from extract import fetch_tcmb_series
    from transform import transform_pipeline
    
    # Test
    df = fetch_tcmb_series("TP.DK.USD.S", "2026-03-01")
    result = transform_pipeline(df)
    validation = run_validation(result['daily'])
