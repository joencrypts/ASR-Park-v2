from datetime import datetime, timedelta
import pytz

def get_ist_time(dt=None):
    """
    Convert datetime to IST (Indian Standard Time) +05:30
    If no datetime provided, returns current IST time
    """
    if dt is None:
        dt = datetime.utcnow()
    
    # Add 5 hours 30 minutes for IST
    ist_offset = timedelta(hours=5, minutes=30)
    ist_time = dt + ist_offset
    
    return ist_time

def format_ist_time(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """
    Format datetime in IST timezone
    """
    ist_time = get_ist_time(dt)
    return ist_time.strftime(format_str)

def format_ist_time_short(dt):
    """
    Format datetime in IST for short display (HH:MM)
    """
    return format_ist_time(dt, '%H:%M')

def format_ist_time_medium(dt):
    """
    Format datetime in IST for medium display (YYYY-MM-DD HH:MM)
    """
    return format_ist_time(dt, '%Y-%m-%d %H:%M')

def format_ist_time_full(dt):
    """
    Format datetime in IST for full display (YYYY-MM-DD HH:MM:SS)
    """
    return format_ist_time(dt, '%Y-%m-%d %H:%M:%S')

def format_ist_date(dt):
    """
    Format date in IST (YYYY-MM-DD)
    """
    return format_ist_time(dt, '%Y-%m-%d')

def format_ist_date_short(dt):
    """
    Format date in IST short format (DD/MM/YYYY)
    """
    return format_ist_time(dt, '%d/%m/%Y')

def format_ist_time_receipt(dt):
    """
    Format time for receipts (HH:MM:SS)
    """
    return format_ist_time(dt, '%H:%M:%S')

def format_ist_receipt_id(dt):
    """
    Format datetime for receipt ID (YYYYMMDDHHMMSS)
    """
    return format_ist_time(dt, '%Y%m%d%H%M%S')

def get_current_ist():
    """
    Get current IST time
    """
    return get_ist_time() 