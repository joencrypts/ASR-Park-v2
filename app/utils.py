from datetime import datetime, timedelta
import pytz

def get_ist_timezone():
    """
    Get IST timezone object
    """
    return pytz.timezone('Asia/Kolkata')

def get_current_ist():
    """
    Get current IST time
    """
    ist_tz = get_ist_timezone()
    return datetime.now(ist_tz)

def get_current_ist_date():
    """
    Get current IST date
    """
    return get_current_ist().date()

def get_ist_time(dt=None):
    """
    Convert datetime to IST (Indian Standard Time) +05:30
    If no datetime provided, returns current IST time
    """
    ist_tz = get_ist_timezone()
    
    if dt is None:
        return datetime.now(ist_tz)
    
    # If dt is naive (no timezone), assume it's in IST
    if dt.tzinfo is None:
        return ist_tz.localize(dt)
    
    # If dt has timezone, convert to IST
    return dt.astimezone(ist_tz)

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

# Legacy functions - now use IST instead of device time
def get_current_device_time():
    """
    Get current IST time (legacy function, now uses IST)
    """
    return get_current_ist()

def get_device_time(dt=None):
    """
    Get IST time (legacy function, now uses IST)
    """
    return get_ist_time(dt)

def format_device_time(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """
    Format datetime in IST (legacy function, now uses IST)
    """
    return format_ist_time(dt, format_str)

def format_device_time_short(dt):
    """
    Format datetime in IST for short display (legacy function, now uses IST)
    """
    return format_ist_time_short(dt)

def format_device_time_medium(dt):
    """
    Format datetime in IST for medium display (legacy function, now uses IST)
    """
    return format_ist_time_medium(dt)

def format_device_time_full(dt):
    """
    Format datetime in IST for full display (legacy function, now uses IST)
    """
    return format_ist_time_full(dt)

def format_device_date(dt):
    """
    Format date in IST (legacy function, now uses IST)
    """
    return format_ist_date(dt)

def format_device_date_short(dt):
    """
    Format date in IST short format (legacy function, now uses IST)
    """
    return format_ist_date_short(dt)

def format_device_time_receipt(dt):
    """
    Format time for receipts in IST (legacy function, now uses IST)
    """
    return format_ist_time_receipt(dt)

def format_device_receipt_id(dt):
    """
    Format datetime for receipt ID in IST (legacy function, now uses IST)
    """
    return format_ist_receipt_id(dt)
