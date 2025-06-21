from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user, login_user, logout_user
from app.models import User, Entry
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_
from app.utils import get_current_device_time, get_ist_time, format_ist_time_full, format_ist_time_medium, format_ist_time_short, format_ist_date, format_ist_date_short, format_ist_time_receipt, format_ist_receipt_id
import qrcode
import io
import base64
import pandas as pd
import tempfile
import os
import json

main = Blueprint('main', __name__)

# Route to serve static files from public directory
@main.route('/public/<path:filename>')
def public_file(filename):
    """Serve static files from the public directory"""
    public_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public')
    return send_file(os.path.join(public_dir, filename))

@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html', title='Home')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        else:
            return redirect(url_for('main.staff_dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            else:
                return redirect(url_for('main.staff_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    
    return render_template('login.html', title='Login')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Check if username already exists
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('Username already taken. Please choose a different username.', 'error')
            return render_template('register.html', title='Register')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('register.html', title='Register')
        
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return render_template('register.html', title='Register')
        
        # Create new user (default role is 'staff')
        new_user = User(username=username, email=email, role='staff')
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html', title='Register')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    vehicle_type_filter = request.args.get('vehicle_type')
    
    # Build query with filters
    query = Entry.query
    
    if start_date:
        query = query.filter(Entry.entry_time >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Entry.entry_time <= datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
    if vehicle_type_filter and vehicle_type_filter != 'all':
        query = query.filter(Entry.vehicle_type == vehicle_type_filter)
    
    # Get all entries for the filtered period
    entries = query.all()
    
    # Calculate statistics
    total_vehicles = len(entries)
    active_parking = len([e for e in entries if not e.exit_time])
    total_revenue = sum([e.amount or 0 for e in entries if e.paid])
    vehicles_exited = len([e for e in entries if e.exit_time])
    
    # Get unique vehicle types for filter dropdown
    vehicle_types = db.session.query(Entry.vehicle_type).distinct().all()
    vehicle_types = [vt[0] for vt in vehicle_types if vt[0]]
    
    # Get recent entries for the table (last 20 entries)
    recent_entries = Entry.query.order_by(Entry.entry_time.desc()).limit(20).all()
    
    # Prepare chart data
    chart_data = prepare_chart_data(entries)
    
    return render_template('admin_dashboard.html', 
                         title='Admin Dashboard',
                         total_vehicles=total_vehicles,
                         active_parking=active_parking,
                         total_revenue=total_revenue,
                         vehicles_exited=vehicles_exited,
                         vehicle_types=vehicle_types,
                         recent_entries=recent_entries,
                         chart_data=chart_data,
                         start_date=start_date,
                         end_date=end_date,
                         vehicle_type_filter=vehicle_type_filter)

@main.route('/admin/export-logs')
@login_required
def export_logs():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    # Get filter parameters from query string
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    vehicle_type_filter = request.args.get('vehicle_type')
    
    # Build query with filters (same as dashboard)
    query = Entry.query
    
    if start_date:
        query = query.filter(Entry.entry_time >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Entry.entry_time <= datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
    if vehicle_type_filter and vehicle_type_filter != 'all':
        query = query.filter(Entry.vehicle_type == vehicle_type_filter)
    
    # Get all entries
    entries = query.order_by(Entry.entry_time.desc()).all()
    
    # Prepare data for Excel
    data = []
    for entry in entries:
        # Calculate duration if exit time exists
        duration = None
        if entry.exit_time:
            entry_time_aware = get_ist_time(entry.entry_time)
            exit_time_aware = get_ist_time(entry.exit_time)
            duration_td = exit_time_aware - entry_time_aware
            duration = str(duration_td).split('.')[0]  # Remove microseconds
        
        data.append({
            'Ticket Number': entry.ticket_number,
            'Vehicle Type': entry.vehicle_type,
            'Vehicle Number': entry.vehicle_number,
            'Phone': entry.phone,
            'Entry Time': format_ist_time_full(entry.entry_time),
            'Exit Time': format_ist_time_full(entry.exit_time) if entry.exit_time else 'Active',
            'Duration': duration or 'Active',
            'Amount (₹)': entry.amount if entry.amount else 0,
            'Payment Status': 'Paid' if entry.paid else 'Unpaid',
            'Device': entry.device
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    
    # Create Excel writer with openpyxl engine
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Parking Logs', index=False)
        
        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Parking Logs']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Add header styling
        from openpyxl.styles import Font, PatternFill, Alignment
        
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
    
    output.seek(0)
    
    # Generate filename with timestamp and filters
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"parking_logs_{timestamp}.xlsx"
    
    # Add filter info to filename if filters are applied
    if start_date or end_date or (vehicle_type_filter and vehicle_type_filter != 'all'):
        filter_parts = []
        if start_date:
            filter_parts.append(f"from_{start_date}")
        if end_date:
            filter_parts.append(f"to_{end_date}")
        if vehicle_type_filter and vehicle_type_filter != 'all':
            filter_parts.append(f"type_{vehicle_type_filter}")
        filename = f"parking_logs_{'_'.join(filter_parts)}_{timestamp}.xlsx"
    
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

def prepare_chart_data(entries):
    """Prepare data for Chart.js visualizations"""
    
    # Vehicle types bar chart
    vehicle_type_counts = {}
    for entry in entries:
        vehicle_type_counts[entry.vehicle_type] = vehicle_type_counts.get(entry.vehicle_type, 0) + 1
    
    # Payment status pie chart
    paid_count = len([e for e in entries if e.paid])
    unpaid_count = len([e for e in entries if not e.paid])
    
    # Revenue over time line chart (last 7 days)
    revenue_data = []
    for i in range(7):
        date_obj = date.today() - timedelta(days=i)
        day_entries = [e for e in entries if e.entry_time.date() == date_obj and e.paid]
        daily_revenue = sum([e.amount or 0 for e in day_entries])
        revenue_data.append({
            'date': date_obj.strftime('%Y-%m-%d'),
            'revenue': daily_revenue
        })
    
    revenue_data.reverse()  # Show oldest to newest
    
    return {
        'vehicle_types': {
            'labels': list(vehicle_type_counts.keys()),
            'data': list(vehicle_type_counts.values())
        },
        'payment_status': {
            'labels': ['Paid', 'Unpaid'],
            'data': [paid_count, unpaid_count]
        },
        'revenue_timeline': {
            'labels': [item['date'] for item in revenue_data],
            'data': [item['revenue'] for item in revenue_data]
        }
    }

@main.route('/staff/dashboard')
@login_required
def staff_dashboard():
    if current_user.role != 'staff':
        flash('Access denied. Staff privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    # Get current time and 24 hours ago
    now = get_current_device_time()
    twenty_four_hours_ago = now - timedelta(hours=24)
    
    # Get vehicles entered in the past 24 hours
    vehicles_entered_24h = Entry.query.filter(
        Entry.entry_time >= twenty_four_hours_ago
    ).count()
    
    # Get active vehicles (entries without exit time)
    active_vehicles = Entry.query.filter(
        Entry.exit_time.is_(None)
    ).count()
    
    # Get vehicles exited in the past 24 hours
    vehicles_exited_24h = Entry.query.filter(
        Entry.exit_time >= twenty_four_hours_ago
    ).count()
    
    # Get exit vehicles (vehicles processed for exit today) - keeping for backward compatibility
    today = date.today()
    exit_vehicles = Entry.query.filter(
        db.func.date(Entry.exit_time) == today
    ).all()
    
    return render_template('staff_dashboard.html', 
                         title='Staff Dashboard',
                         vehicles_entered_24h=vehicles_entered_24h,
                         active_vehicles=active_vehicles,
                         vehicles_exited_24h=vehicles_exited_24h,
                         exit_vehicles=exit_vehicles)

@main.route('/staff/active-vehicles')
@login_required
def active_vehicles():
    if current_user.role not in ['admin', 'staff']:
        flash('Access denied. Staff or Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    # Get active vehicles (entries without exit time)
    active_vehicles = Entry.query.filter(
        Entry.exit_time.is_(None)
    ).order_by(Entry.entry_time.desc()).all()
    
    return render_template('active_vehicles.html', 
                         title='Active Vehicles',
                         active_vehicles=active_vehicles)

@main.route('/staff/exited-vehicles')
@login_required
def exited_vehicles():
    if current_user.role not in ['admin', 'staff']:
        flash('Access denied. Staff or Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    # Get exited vehicles (entries with exit time)
    exited_vehicles = Entry.query.filter(
        Entry.exit_time.is_not(None)
    ).order_by(Entry.exit_time.desc()).limit(50).all()
    
    return render_template('exited_vehicles.html', 
                         title='Exited Vehicles',
                         exited_vehicles=exited_vehicles)

@main.route('/staff/vehicle-entry', methods=['GET', 'POST'])
@login_required
def vehicle_entry():
    if current_user.role not in ['admin', 'staff']:
        flash('Access denied. Staff or Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        vehicle_type = request.form.get('vehicle_type')
        vehicle_number = request.form.get('vehicle_number')
        phone = request.form.get('phone')
        device = f'Terminal - {current_user.username}'  # Include user username
        
        # Normalize phone number (remove spaces, dashes, and other characters)
        phone = ''.join(filter(str.isdigit, phone))
        
        # Handle cycle token number generation
        if vehicle_type == 'Cycle':
            # Auto-generate cycle token number
            vehicle_number = generate_cycle_token()
        else:
            # Normalize vehicle number (remove spaces, convert to uppercase)
            vehicle_number = vehicle_number.replace(' ', '').upper()
        
        # Check if vehicle/token is already parked
        existing_entry = Entry.query.filter_by(
            vehicle_number=vehicle_number, 
            paid=False
        ).first()
        
        if existing_entry:
            if vehicle_type == 'Cycle':
                flash(f'Cycle token {vehicle_number} is already parked. Please process exit first.', 'error')
            else:
                flash(f'Vehicle {vehicle_number} is already parked. Please process exit first.', 'error')
            return render_template('vehicle_entry.html', title='Register Vehicle')
        
        # Generate ticket number with ASR prefix (reset daily)
        today = date.today()
        
        # Find the highest ticket number for today
        today_tickets = Entry.query.filter(
            db.func.date(Entry.entry_time) == today
        ).with_entities(Entry.ticket_number).all()
        
        if today_tickets:
            # Extract numbers from existing ticket numbers and find the max
            ticket_numbers = []
            for ticket in today_tickets:
                if ticket[0].startswith('ASR'):
                    try:
                        ticket_numbers.append(int(ticket[0].replace('ASR', '')))
                    except ValueError:
                        continue
            next_number = max(ticket_numbers) + 1 if ticket_numbers else 1
        else:
            # If no tickets today, start from 1
            next_number = 1
        
        # Format: ASR00001, ASR00002, etc. (resets daily)
        ticket_number = f"ASR{next_number:05d}"
        
        # Double-check that this ticket number doesn't exist anywhere in the database
        existing_ticket = Entry.query.filter_by(ticket_number=ticket_number).first()
        if existing_ticket:
            # Find the next available number by checking all existing tickets
            all_tickets = Entry.query.with_entities(Entry.ticket_number).all()
            all_numbers = []
            for ticket in all_tickets:
                if ticket[0].startswith('ASR'):
                    try:
                        all_numbers.append(int(ticket[0].replace('ASR', '')))
                    except ValueError:
                        continue
            
            if all_numbers:
                next_number = max(all_numbers) + 1
            else:
                next_number = 1
            
            ticket_number = f"ASR{next_number:05d}"
        
        # Create new entry
        new_entry = Entry(
            ticket_number=ticket_number,
            vehicle_type=vehicle_type,
            vehicle_number=vehicle_number,
            phone=phone,
            device=device,
            entry_time=get_current_device_time()
        )
        
        db.session.add(new_entry)
        db.session.commit()
        
        # Generate QR code with ticket number and entry time
        qr_data = {
            'ticket': ticket_number,
            'entry_time': new_entry.entry_time.isoformat(),
            'vehicle_number': vehicle_number
        }
        qr_json = json.dumps(qr_data)
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_json)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for display
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        
        flash('Vehicle registered successfully!', 'success')
        return render_template('vehicle_entry_success.html', 
                             title='Vehicle Registered',
                             ticket_number=ticket_number,
                             qr_code=img_str,
                             entry=new_entry)
    
    return render_template('vehicle_entry.html', title='Register Vehicle')

@main.route('/staff/vehicle-entry/success')
@login_required
def vehicle_entry_success():
    if current_user.role not in ['admin', 'staff']:
        flash('Access denied. Staff or Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    return render_template('vehicle_entry_success.html', title='Vehicle Registered')

@main.route('/staff/vehicle-exit', methods=['GET', 'POST'])
@login_required
def vehicle_exit():
    if current_user.role not in ['admin', 'staff']:
        flash('Access denied. Staff or Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        search_type = request.form.get('search_type')
        search_value = request.form.get('search_value')
        
        if search_type == 'qr_code':
            # Parse QR code JSON data
            try:
                qr_data = json.loads(search_value)
                ticket_number = qr_data.get('ticket')
                entry_time_str = qr_data.get('entry_time')
                qr_vehicle_number = qr_data.get('vehicle_number')
                
                if not ticket_number:
                    flash('Invalid QR code: Missing ticket number.', 'error')
                    return render_template('vehicle_exit.html', title='Vehicle Exit')
                
                # Search by ticket number
                entry = Entry.query.filter_by(ticket_number=ticket_number, paid=False).first()
                
                if not entry:
                    flash('No active parking found for this ticket.', 'error')
                    return render_template('vehicle_exit.html', title='Vehicle Exit')
                
                # Validate entry time if provided in QR
                if entry_time_str:
                    try:
                        qr_entry_time = datetime.fromisoformat(entry_time_str)
                        # Make both times timezone-aware for comparison
                        qr_entry_time_aware = get_ist_time(qr_entry_time)
                        entry_time_aware = get_ist_time(entry.entry_time)
                        if abs((entry_time_aware - qr_entry_time_aware).total_seconds()) > 60:  # Allow 1 minute difference
                            flash('QR code entry time does not match database record.', 'error')
                            return render_template('vehicle_exit.html', title='Vehicle Exit')
                    except ValueError:
                        flash('Invalid entry time in QR code.', 'error')
                        return render_template('vehicle_exit.html', title='Vehicle Exit')
                
                # Validate vehicle number if provided in QR
                if qr_vehicle_number and entry.vehicle_number != qr_vehicle_number:
                    flash('QR code vehicle number does not match database record.', 'error')
                    return render_template('vehicle_exit.html', title='Vehicle Exit')
                    
            except json.JSONDecodeError:
                # Fallback: try to use as plain ticket number (backward compatibility)
                entry = Entry.query.filter_by(ticket_number=search_value, paid=False).first()
                if not entry:
                    flash('Invalid QR code format or no active parking found.', 'error')
                    return render_template('vehicle_exit.html', title='Vehicle Exit')
        elif search_type == 'phone':
            # Search by phone number (normalize the search value)
            normalized_phone = ''.join(filter(str.isdigit, search_value))
            
            # Check if there are multiple vehicles with this phone number
            vehicles_with_phone = Entry.query.filter_by(phone=normalized_phone, paid=False).all()
            
            if not vehicles_with_phone:
                flash('No active parking found for this phone number.', 'error')
                return render_template('vehicle_exit.html', title='Vehicle Exit')
            
            if len(vehicles_with_phone) == 1:
                # Only one vehicle, proceed directly
                entry = vehicles_with_phone[0]
            else:
                # Multiple vehicles found, show selection page
                # Calculate duration for each vehicle
                current_time = get_current_device_time()
                vehicles_with_duration = []
                for vehicle in vehicles_with_phone:
                    entry_time_aware = get_ist_time(vehicle.entry_time)
                    duration = current_time - entry_time_aware
                    hours = duration.total_seconds() / 3600
                    vehicles_with_duration.append({
                        'vehicle': vehicle,
                        'hours': hours
                    })
                
                return render_template('vehicle_selection.html', 
                                     title='Select Vehicle',
                                     vehicles_with_duration=vehicles_with_duration,
                                     phone_number=normalized_phone)
        else:
            # Search by vehicle number/token (normalize the search value)
            normalized_search = search_value.replace(' ', '').upper()
            entry = Entry.query.filter_by(vehicle_number=normalized_search, paid=False).first()
        
        if not entry:
            flash('No active parking found for the provided information.', 'error')
            return render_template('vehicle_exit.html', title='Vehicle Exit')
        
        if entry.exit_time:
            if entry.vehicle_type == 'Cycle':
                flash('Cycle has already been processed for exit.', 'error')
            else:
                flash('Vehicle has already been processed for exit.', 'error')
            return render_template('vehicle_exit.html', title='Vehicle Exit')
        
        # Calculate bill
        exit_time = get_current_device_time()
        # Ensure entry_time is timezone-aware for calculation
        entry_time_aware = get_ist_time(entry.entry_time)
        duration = exit_time - entry_time_aware
        hours = duration.total_seconds() / 3600
        
        # Calculate charges using daily rates
        total_amount, total_days = calculate_daily_charges(entry_time_aware, exit_time, entry.vehicle_type)
        
        # Update entry with exit time and amount
        entry.exit_time = exit_time
        entry.amount = total_amount
        entry.device = f'Exit Terminal - {current_user.username}'  # Update device with exit user
        
        db.session.commit()
        
        return render_template('payment_page.html', 
                             title='Payment',
                             entry=entry,
                             hours=hours,
                             days=total_days,
                             total_amount=total_amount)
    
    return render_template('vehicle_exit.html', title='Vehicle Exit')

@main.route('/staff/select-vehicle/<int:entry_id>')
@login_required
def select_vehicle(entry_id):
    """Process exit for a specific vehicle selected from multiple options"""
    if current_user.role not in ['admin', 'staff']:
        flash('Access denied. Staff or Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    entry = Entry.query.get_or_404(entry_id)
    
    if entry.paid:
        flash('This vehicle has already been processed for exit.', 'error')
        return redirect(url_for('main.vehicle_exit'))
    
    if entry.exit_time:
        if entry.vehicle_type == 'Cycle':
            flash('Cycle has already been processed for exit.', 'error')
        else:
            flash('Vehicle has already been processed for exit.', 'error')
        return redirect(url_for('main.vehicle_exit'))
    
    # Calculate bill
    exit_time = get_current_device_time()
    # Ensure entry_time is timezone-aware for calculation
    entry_time_aware = get_ist_time(entry.entry_time)
    duration = exit_time - entry_time_aware
    hours = duration.total_seconds() / 3600
    
    # Calculate charges using daily rates
    total_amount, total_days = calculate_daily_charges(entry_time_aware, exit_time, entry.vehicle_type)
    
    # Update entry with exit time and amount
    entry.exit_time = exit_time
    entry.amount = total_amount
    entry.device = f'Exit Terminal - {current_user.username}'  # Update device with exit user
    
    db.session.commit()
    
    return render_template('payment_page.html', 
                         title='Payment',
                         entry=entry,
                         hours=hours,
                         days=total_days,
                         total_amount=total_amount)

@main.route('/staff/process-payment/<int:entry_id>', methods=['POST'])
@login_required
def process_payment(entry_id):
    if current_user.role not in ['admin', 'staff']:
        flash('Access denied. Staff or Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    entry = Entry.query.get_or_404(entry_id)
    
    if entry.paid:
        flash('Payment has already been processed for this vehicle.', 'error')
        return redirect(url_for('main.vehicle_exit'))
    
    # Mark as paid
    entry.paid = True
    db.session.commit()
    
    flash('Payment processed successfully! Vehicle can now exit.', 'success')
    return redirect(url_for('main.payment_success', entry_id=entry.id))

@main.route('/staff/payment-success/<int:entry_id>')
@login_required
def payment_success(entry_id):
    if current_user.role not in ['admin', 'staff']:
        flash('Access denied. Staff or Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    entry = Entry.query.get_or_404(entry_id)
    return render_template('payment_success.html', 
                         title='Payment Successful',
                         entry=entry)

@main.route('/receipt/<int:entry_id>')
@login_required
def print_receipt(entry_id):
    if current_user.role not in ['admin', 'staff']:
        flash('Access denied. Staff or Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    entry = Entry.query.get_or_404(entry_id)
    
    # Generate QR code with ticket number and entry time
    qr_data = {
        'ticket': entry.ticket_number,
        'entry_time': entry.entry_time.isoformat(),
        'vehicle_number': entry.vehicle_number
    }
    qr_json = json.dumps(qr_data)
    
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(qr_json)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for display
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    qr_code = base64.b64encode(img_buffer.getvalue()).decode()
    
    return render_template('thermal_receipt.html', 
                         entry=entry, 
                         qr_code=qr_code)

@main.route('/receipt/ticket/<ticket_number>')
def public_receipt(ticket_number):
    """Public route to view receipt by ticket number (no login required)"""
    entry = Entry.query.filter_by(ticket_number=ticket_number).first_or_404()
    
    # Generate QR code with ticket number and entry time
    qr_data = {
        'ticket': entry.ticket_number,
        'entry_time': entry.entry_time.isoformat(),
        'vehicle_number': entry.vehicle_number
    }
    qr_json = json.dumps(qr_data)
    
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(qr_json)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for display
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    qr_code = base64.b64encode(img_buffer.getvalue()).decode()
    
    return render_template('thermal_receipt.html', 
                         entry=entry, 
                         qr_code=qr_code)

@main.route('/exit-receipt/<int:entry_id>')
@login_required
def exit_receipt(entry_id):
    """Print exit receipt with exit bill format"""
    if current_user.role not in ['admin', 'staff']:
        flash('Access denied. Staff or Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    entry = Entry.query.get_or_404(entry_id)
    
    if not entry.exit_time:
        flash('Vehicle has not been processed for exit yet.', 'error')
        return redirect(url_for('main.vehicle_exit'))
    
    # Calculate charges using daily rates
    total_amount, total_days = calculate_daily_charges(entry.entry_time, entry.exit_time, entry.vehicle_type)
    
    # Calculate duration with timezone-aware datetimes
    entry_time_aware = get_ist_time(entry.entry_time)
    exit_time_aware = get_ist_time(entry.exit_time)
    duration = exit_time_aware - entry_time_aware
    hours = duration.total_seconds() / 3600
    
    return render_template('exit_receipt.html', 
                         entry=entry,
                         total_amount=total_amount,
                         days=total_days,
                         hours=hours)

@main.route('/admin/users')
@login_required
def manage_users():
    """Admin page to manage users (add/remove admins and staff)"""
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    return render_template('manage_users.html', 
                         title='Manage Users',
                         users=users)

@main.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    """Add new user (admin or staff)"""
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # Validate input
        if not username or not email or not password or not role:
            flash('All fields are required.', 'error')
            return render_template('add_user.html', title='Add User')
        
        if role not in ['admin', 'staff']:
            flash('Invalid role selected.', 'error')
            return render_template('add_user.html', title='Add User')
        
        # Check if username already exists
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('Username already taken. Please choose a different username.', 'error')
            return render_template('add_user.html', title='Add User')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('User with this email already exists.', 'error')
            return render_template('add_user.html', title='Add User')
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            role=role
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'User {email} added successfully as {role}.', 'success')
        return redirect(url_for('main.manage_users'))
    
    return render_template('add_user.html', title='Add User')

@main.route('/admin/users/remove/<int:user_id>', methods=['POST'])
@login_required
def remove_user(user_id):
    """Remove user (admin or staff)"""
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    # Prevent admin from removing themselves
    if user_id == current_user.id:
        flash('You cannot remove your own account.', 'error')
        return redirect(url_for('main.manage_users'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent removing the last admin
    if user.role == 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            flash('Cannot remove the last admin account.', 'error')
            return redirect(url_for('main.manage_users'))
    
    email = user.email
    role = user.role
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {email} ({role}) removed successfully.', 'success')
    return redirect(url_for('main.manage_users'))

@main.route('/admin/staff-progress')
@login_required
def staff_progress():
    """Admin view of staff performance and progress"""
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    # Get all staff members
    staff_members = User.query.filter_by(role='staff').all()
    
    # Get current time and 24 hours ago
    now = get_current_device_time()
    twenty_four_hours_ago = now - timedelta(hours=24)
    
    # Calculate staff performance
    staff_data = []
    for staff in staff_members:
        # Count entries in the past 24 hours by this staff
        entries_24h = Entry.query.filter(
            Entry.entry_time >= twenty_four_hours_ago,
            (Entry.device == f'Terminal - {staff.username}') |
            (Entry.device == f'Exit Terminal - {staff.username}')
        ).count()
        
        # Count exits processed in the past 24 hours by this staff
        exits_24h = Entry.query.filter(
            Entry.exit_time >= twenty_four_hours_ago,
            Entry.device == f'Exit Terminal - {staff.username}'
        ).count()
        
        # Total entries by this staff
        total_entries = Entry.query.filter(
            (Entry.device == f'Terminal - {staff.username}') |
            (Entry.device == f'Exit Terminal - {staff.username}')
        ).count()
        
        # Total exits processed by this staff
        total_exits = Entry.query.filter(
            Entry.exit_time.isnot(None),
            Entry.device == f'Exit Terminal - {staff.username}'
        ).count()
        
        staff_data.append({
            'user': staff,
            'entries_24h': entries_24h,
            'exits_24h': exits_24h,
            'total_entries': total_entries,
            'total_exits': total_exits
        })
    
    return render_template('staff_progress.html', 
                         title='Staff Progress',
                         staff_data=staff_data)

@main.route('/admin/staff-details/<int:staff_id>')
@login_required
def staff_details(staff_id):
    """Detailed view of individual staff member's entries and progress"""
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    staff = User.query.get_or_404(staff_id)
    if staff.role != 'staff':
        flash('User is not a staff member.', 'error')
        return redirect(url_for('main.staff_progress'))
    
    # Get current time and 24 hours ago
    now = get_current_device_time()
    twenty_four_hours_ago = now - timedelta(hours=24)
    
    # Get recent entries by this staff (last 50)
    recent_entries = Entry.query.filter(
        (Entry.device == f'Terminal - {staff.username}') |
        (Entry.device == f'Exit Terminal - {staff.username}')
    ).order_by(Entry.entry_time.desc()).limit(50).all()
    
    # Get recent exits by this staff (last 50)
    recent_exits = Entry.query.filter(
        Entry.exit_time.isnot(None),
        Entry.device == f'Exit Terminal - {staff.username}'
    ).order_by(Entry.exit_time.desc()).limit(50).all()
    
    # Calculate statistics
    entries_24h = Entry.query.filter(
        Entry.entry_time >= twenty_four_hours_ago,
        (Entry.device == f'Terminal - {staff.username}') |
        (Entry.device == f'Exit Terminal - {staff.username}')
    ).count()
    
    exits_24h = Entry.query.filter(
        Entry.exit_time >= twenty_four_hours_ago,
        Entry.device == f'Exit Terminal - {staff.username}'
    ).count()
    
    total_entries = Entry.query.filter(
        (Entry.device == f'Terminal - {staff.username}') |
        (Entry.device == f'Exit Terminal - {staff.username}')
    ).count()
    
    total_exits = Entry.query.filter(
        Entry.exit_time.isnot(None),
        Entry.device == f'Exit Terminal - {staff.username}'
    ).count()
    
    # Calculate efficiency rate
    efficiency_rate = 0
    if total_entries > 0:
        efficiency_rate = (total_exits / total_entries) * 100
    
    return render_template('staff_details.html',
                         title=f'Staff Details - {staff.username}',
                         staff=staff,
                         recent_entries=recent_entries,
                         recent_exits=recent_exits,
                         entries_24h=entries_24h,
                         exits_24h=exits_24h,
                         total_entries=total_entries,
                         total_exits=total_exits,
                         efficiency_rate=efficiency_rate)

@main.route('/admin/clear-entries', methods=['GET', 'POST'])
@login_required
def clear_entries():
    """Admin function to clear all vehicle entries"""
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Get confirmation and date range
        confirmation = request.form.get('confirmation')
        clear_type = request.form.get('clear_type')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        if confirmation != 'CLEAR':
            flash('Please type "CLEAR" to confirm the operation.', 'error')
            return render_template('clear_entries.html', title='Clear Entries')
        
        try:
            if clear_type == 'all':
                # Clear all entries
                deleted_count = Entry.query.delete()
                db.session.commit()
                flash(f'All {deleted_count} vehicle entries have been cleared.', 'success')
                
            elif clear_type == 'date_range' and start_date and end_date:
                # Clear entries within date range
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                
                deleted_count = Entry.query.filter(
                    Entry.entry_time >= start_dt,
                    Entry.entry_time < end_dt
                ).delete()
                db.session.commit()
                flash(f'{deleted_count} vehicle entries from {start_date} to {end_date} have been cleared.', 'success')
                
            elif clear_type == 'paid_only':
                # Clear only paid entries
                deleted_count = Entry.query.filter_by(paid=True).delete()
                db.session.commit()
                flash(f'{deleted_count} paid vehicle entries have been cleared.', 'success')
                
            else:
                flash('Invalid clear type selected.', 'error')
                return render_template('clear_entries.html', title='Clear Entries')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error clearing entries: {str(e)}', 'error')
            return render_template('clear_entries.html', title='Clear Entries')
        
        return redirect(url_for('main.admin_dashboard'))
    
    return render_template('clear_entries.html', title='Clear Entries')

def generate_cycle_token():
    """
    Generate cycle token number from CYC001 to CYC999, then reset to CYC001
    """
    # Get all existing cycle tokens
    cycle_entries = Entry.query.filter(
        Entry.vehicle_type == 'Cycle'
    ).with_entities(Entry.vehicle_number).all()
    
    cycle_numbers = []
    for entry in cycle_entries:
        vehicle_number = entry[0]
        if vehicle_number.startswith('CYC'):
            try:
                # Extract number from CYC001 format
                number = int(vehicle_number[3:])
                cycle_numbers.append(number)
            except ValueError:
                continue
    
    if cycle_numbers:
        # Find the next available number
        max_number = max(cycle_numbers)
        next_number = max_number + 1
        
        # If we've reached 999, reset to 1
        if next_number > 999:
            next_number = 1
    else:
        # No existing cycles, start from 1
        next_number = 1
    
    return f"CYC{next_number:03d}" 

def calculate_daily_charges(entry_time, exit_time, vehicle_type):
    """
    Calculate charges based on daily rates (midnight to midnight)
    """
    # Updated base charges per day
    daily_charges = {
        'Bike': 10,
        'Car': 50,
        'Auto': 25,
        'Cycle': 5,
        'Van': 100,
        'Tembo': 100,
        'Lorry': 150,
        'Bus': 150
    }
    
    base_amount = daily_charges.get(vehicle_type, 50)
    
    # Ensure both times are timezone-aware and in IST
    from app.utils import get_ist_time
    entry_time_aware = get_ist_time(entry_time)
    exit_time_aware = get_ist_time(exit_time)
    
    # Get entry and exit dates (midnight to midnight) in IST
    entry_date = entry_time_aware.date()
    exit_date = exit_time_aware.date()
    
    # Calculate number of days
    days_diff = (exit_date - entry_date).days
    
    # Debug information (you can remove this after testing)
    print(f"DEBUG: Entry time: {entry_time_aware}, Entry date: {entry_date}")
    print(f"DEBUG: Exit time: {exit_time_aware}, Exit date: {exit_date}")
    print(f"DEBUG: Days difference: {days_diff}")
    
    # If same day, charge for 1 day
    if days_diff == 0:
        return base_amount, 1
    
    # If different days, charge for each day
    total_days = days_diff + 1
    total_amount = base_amount * total_days
    
    return total_amount, total_days 
