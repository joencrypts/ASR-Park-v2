# ASR Parking Lot Management System

A comprehensive parking lot management system built with Flask, featuring role-based access control, QR code generation, vehicle tracking, and automated billing.

## Features

- **Role-Based Access Control**: Admin and Staff roles with different permissions
- **Vehicle Entry/Exit Management**: Complete vehicle lifecycle tracking
- **QR Code Integration**: Generate and scan QR codes for tickets
- **Automated Billing**: Calculate parking fees based on duration
- **Real-time Dashboard**: Live statistics and progress tracking
- **Staff Performance Tracking**: Monitor individual staff contributions
- **Export Functionality**: Export data to Excel format
- **Responsive Design**: Works on all devices and screen orientations
- **Thermal Printer Support**: Optimized receipts for thermal printers

## Technology Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript
- **QR Codes**: qrcode[pil]
- **Data Export**: pandas, openpyxl
- **Production**: Gunicorn

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/joencrypts/ASR-Final.git
   cd ASR-Final
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python init_db.py
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Register a new admin account to get started

## Usage

### Admin Features
- View comprehensive dashboard with statistics
- Manage staff members
- Track staff performance and progress
- Export data to Excel
- View all vehicle entries and exits
- Clear database entries

### Staff Features
- Register new vehicle entries
- Process vehicle exits and payments
- Generate QR codes for tickets
- Print receipts
- View active vehicles
- Track personal performance

## Deployment

### Render Deployment
This project is configured for easy deployment on Render:

1. **Fork/Clone** this repository
2. **Connect** to Render dashboard
3. **Create** a new Web Service
4. **Select** the repository
5. **Deploy** automatically

The project includes:
- `Procfile` for Render deployment
- `render.yaml` for configuration
- `requirements.txt` with all dependencies

### Environment Variables
Set these in your Render dashboard:
- `FLASK_ENV=production`
- `FLASK_DEBUG=false`

## Project Structure

```
ASR-Final/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── routes.py            # Application routes
│   ├── static/              # Static files
│   └── templates/           # HTML templates
├── instance/                # Database files
├── public/                  # Public assets (logo, favicon)
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
├── init_db.py              # Database initialization
├── Procfile                # Render deployment
├── render.yaml             # Render configuration
└── README.md               # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For support or questions, please open an issue on GitHub or contact the development team.

---

**ASR Parking Lot Management System** - Efficient parking management for modern facilities. 