# Shift Rota Management System

A comprehensive Flask-based web application for managing employee shift schedules with department-specific authentication and real-time updates.

## 🚀 Features

### 🔐 Authentication System
- **Department-specific login** - Each department has its own password
- **Employee vs Admin access** - Different permission levels
- **Auto-logout** - Session cleared when returning to home
- **Read-only mode** - View schedules without editing
- **2FA Password Reset** - Secure email-based password recovery with tokens
- **Forgot Password** - Multiple recovery options including admin contact

### 📅 Rota Management
- **Monthly view** with complete weekly cycles (Mon-Sun)
- **Real-time color updates** when selecting shifts
- **Shift descriptions** in dropdowns for easy identification
- **Filter by process/employee** and shift types
- **CSV export** functionality
- **Visual shift indicators** with color-coded timing categories

### ⚙️ Administration
- **Employee management** - Add/edit/remove employees by department
- **Shift management** - Configure shift codes and timings
- **Password management** - Change department passwords
- **Settings page** - Centralized administration interface

### 🎨 Modern UI
- **Responsive design** - Works on desktop and mobile
- **Color-coded shifts** by timing (morning=blue, day=orange, night=dark blue)
- **Interactive modals** for department access
- **Sticky table headers** and columns for large schedules
- **Hover effects** and smooth animations

## 📁 Project Structure

```
rota_app/
├── app.py                     # Main Flask application
├── requirements.txt           # Python dependencies
├── start_server.bat          # Windows start script
├── README.md                 # This file
├── static/
│   └── csc-logo.png          # Company logo
├── templates/
│   ├── base.html             # Base template with header/navigation
│   ├── index.html            # Home page with department selection
│   ├── dept.html             # Department rota page
│   ├── department_settings.html # Admin settings page
│   ├── login.html            # Login page
│   └── allowances.html       # Shift allowance calculations
└── data/
    ├── rota_data.json        # Shift assignments data
    └── department_config.json # Department configuration
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Download/Clone the project**
   ```bash
   # If downloaded as ZIP, extract to desired location
   cd rota_app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```
   
   Or on Windows, double-click `start_server.bat`

4. **Access the application**
   - Open your browser to `http://localhost:5000`
   - The application will start with sample data

## 🔑 Default Access

### Department Passwords
- **Service Desk**: `service123`
- **App Tools**: `apptools123`
- **App Development**: `appdev123`
- **Cloud Ops**: `cloudops123`
- **End User Ops**: `enduser123`
- **Messaging**: `messaging123`
- **Network Team**: `network123`
- **Threat Response Team**: `threat123`

### Global Admin
- **Password**: `editor123` (can access all departments)

### Email Configuration (Optional)
For password reset functionality, configure email settings:

1. **Create `.env` file** (copy from `.env.example`)
2. **Set email credentials**:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your-app-email@gmail.com
   SENDER_PASSWORD=your-app-password
   ```
3. **For Gmail**: Use an App Password, not your regular password
   - Generate at: https://myaccount.google.com/apppasswords
4. **Update department admin emails** in `app.py` (`DEPARTMENT_ADMIN_EMAILS`)

## 🎯 How to Use

### For Employees (Read-Only Access)
1. Click on any department from the home page
2. Select "👥 Employee Login" 
3. View the rota schedule without editing

### For Admins (Edit Access)
1. Click on any department from the home page
2. Select "🔑 Admin Login"
3. Enter the department password
4. Edit shifts by clicking on dropdown menus
5. Colors update immediately when you select shifts
6. Click "Save Changes" to persist modifications

### For Department Management
1. Login as admin to any department
2. Click "⚙️ Settings" in the top navigation
3. Manage employees, shifts, and passwords
4. Use the "Back" button to return to the rota

### For Password Recovery
1. Click "Forgot Password?" on the login page
2. Choose from recovery options:
   - **Email Reset**: Send secure token to department admins
   - **Admin Contact**: Direct contact information
   - **Password Hints**: Common password patterns
   - **Emergency Request**: Submit formal access request
3. For email reset: Check admin email for reset link
4. Click link and create new password (link expires in 30 minutes)

## 🎨 Shift Color Coding

### By Timing Category
- **🌅 Early Morning** (APAC, Morning): Light blue
- **🌞 Day Shifts** (General, Afternoon): Light orange  
- **🌙 Evening/Night** (Evening, Night): Dark blue

### By Status
- **PL** (Planned Leave): Light red
- **AL** (Adhoc Leave): Dark red
- **WO** (Weekly Off): Light gray
- **Holiday**: Dark green
- **LWD** (Last Working Day): Purple

## 🔧 Configuration

### Adding New Departments
Edit `app.py` and add to the `DEPARTMENTS` dictionary:
```python
"New Department": {
    "processes": {
        "Process Name": ["Employee1", "Employee2"]
    },
    "shifts": {
        "CODE": "Description"
    },
    "show_filters": True,
    "password": "newdept123"
}
```

### Customizing Shifts
Modify the shifts dictionary for any department:
```python
"shifts": {
    "MORNING": "9AM to 5PM",
    "EVENING": "5PM to 1AM",
    "CUSTOM": "Custom timing"
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   - Change port in `app.py`: `app.run(port=5001)`
   - Or kill existing processes using port 5000

2. **Templates not found**
   - Ensure you're running from the project root directory
   - Check that `templates/` folder exists

3. **Data not persisting**
   - Check write permissions in the `data/` directory
   - Ensure JSON files are valid format

4. **Colors not updating**
   - Hard refresh browser (Ctrl+F5)
   - Check browser console for JavaScript errors

## 📝 Development Notes

### Key Files to Modify
- **app.py**: Backend logic, routes, and data handling
- **templates/base.html**: Global styling and navigation
- **templates/dept.html**: Main rota interface
- **templates/index.html**: Home page and department selection

### Adding New Features
1. Add new routes in `app.py`
2. Create corresponding templates
3. Update navigation in `base.html` if needed
4. Test with different user permissions

## 🚀 Deployment

### Local Development
- Use `python app.py` for development
- Debug mode enabled by default

### Production
- Set environment variables for security
- Use proper WSGI server (gunicorn, uWSGI)
- Configure reverse proxy (nginx)
- Enable HTTPS

## 📄 License

This project is for internal use. Modify as needed for your organization.

## 🆘 Support

For issues or questions:
1. Check this README
2. Review error messages in browser console
3. Check Python console output
4. Verify file permissions and structure

---

**Happy Scheduling! 📅✨**