# Department Management Feature

This document explains the new department management functionality that has been added to the Rota App.

## Overview

The department management feature allows editors to dynamically manage their department's structure through the web interface, including:
- Adding/removing employees organized by process/role
- Adding/removing shift types
- Changing department passwords
- Persistent storage of department configurations

## Features

### 1. Employee Management
- **Add Employee**: Create new employees and assign them to processes/roles
- **Edit Employee**: Modify existing employee names and move them between processes
- **Remove Employee**: Remove employees from processes
- **Process Organization**: Employees are organized by process or role (e.g., "Maintenance", "Operations", "Quality Control")
- **Real-time Updates**: Changes are immediately reflected in the rota views

### 2. Shift Management  
- **Add Shift**: Create new shift types with codes and descriptions
- **Edit Shift**: Modify existing shift codes and descriptions
- **Remove Shift**: Remove existing shift types
- **Custom Shifts**: Each department can have unique shift patterns

### 3. Password Management
- **Department Passwords**: Each department maintains its own login password
- **Admin Access**: System administrators can manage all departments
- **Security**: Non-admin users can only manage their own department

## How to Use

### Initial Setup

1. **Create Configuration File**: Run the sample configuration script to get started:
   ```bash
   python create_sample_config.py
   ```
   This creates a `department_config.json` file with sample departments and data.

2. **Start the Application**: 
   ```bash
   python app.py
   ```

3. **Login**: Use either:
   - System admin password (defined in EDITOR_PASSWORD)
   - Department-specific password (from configuration)

### Accessing Department Settings

1. Login as either a system administrator or department user
2. Navigate to "Department Settings" from the main menu
3. You'll see sections for:
   - Password Management
   - Employee Management  
   - Shift Management

### Managing Employees

**Adding Employees:**
1. Fill out the "Add Employee" form:
   - Select department (if you're an admin)
   - Enter process/role name (e.g., "Maintenance", "Operations")
   - Enter employee name
2. Click "Add Employee"

**Editing Employees:**
1. Use the "Edit Employee" form:
   - Select department (if you're an admin)
   - Select current process from dropdown
   - Select current employee from dropdown
   - Enter new process/role name
   - Enter new employee name
2. Click "Update Employee"

**Removing Employees:**
1. Use the "Remove Employee" form:
   - Select department (if you're an admin)
   - Select process from dropdown
   - Select employee from dropdown
2. Click "Remove Employee"

### Managing Shifts

**Adding Shifts:**
1. Fill out the "Add Shift" form:
   - Select department (if you're an admin)
   - Enter shift code (e.g., "D", "N", "E")
   - Enter shift description (e.g., "Day (6AM-2PM)")
2. Click "Add Shift"

**Editing Shifts:**
1. Use the "Edit Shift" form:
   - Select department (if you're an admin)
   - Select current shift from dropdown
   - Enter new shift code
   - Enter new shift description
2. Click "Update Shift"

**Removing Shifts:**
1. Use the "Remove Shift" form:
   - Select department (if you're an admin)
   - Select shift from dropdown
2. Click "Remove Shift"

### Changing Passwords

1. Use the "Password Management" section
2. Select department (if you're an admin)
3. Enter new password (minimum 6 characters)
4. Confirm password
5. Click "Update Password"

## Technical Details

### File Structure
- `department_config.json`: Main configuration file storing all department data
- `app.py`: Contains the new management routes and functions
- `templates/department_settings.html`: Management interface

### Configuration Format
```json
{
  "Department Name": {
    "password": "department_password",
    "shifts": {
      "D": "Day (6AM-2PM)",
      "N": "Night (10PM-6AM)"
    },
    "processes": {
      "Process Name": ["Employee 1", "Employee 2"]
    }
  }
}
```

### New Routes
- `GET/POST /department-settings`: Main management interface
- All management actions are handled through form submissions with different `action` parameters:
  - `change_password`
  - `add_employee`
  - `edit_employee`
  - `remove_employee`
  - `add_shift`
  - `edit_shift`
  - `remove_shift`

### Security Features
- **Authorization**: Only logged-in users can access settings
- **Department Isolation**: Non-admin users can only manage their own department
- **Input Validation**: All form inputs are validated and sanitized
- **Confirmation Dialogs**: Deletion actions require user confirmation

## Sample Data

The `create_sample_config.py` script creates three sample departments:

1. **Engineering** (password: eng123)
   - Shifts: Day, Night, Evening
   - Processes: Maintenance, Operations, Quality Control

2. **Production** (password: prod456)
   - Shifts: Day, Night, Afternoon  
   - Processes: Assembly, Packaging, Inspection

3. **Administration** (password: admin789)
   - Shifts: Day, Extended
   - Processes: HR, Finance, IT Support

## Migration from Static Configuration

If you're upgrading from the previous static DEPARTMENTS configuration:

1. Your existing department data from `app.py` will still work as a fallback
2. Run `create_sample_config.py` to create the JSON file
3. Copy your existing data to the JSON format
4. The app will automatically use the JSON file when available

## Troubleshooting

### Common Issues

1. **Configuration file not found**: The app falls back to static DEPARTMENTS if JSON file doesn't exist
2. **Permission denied**: Ensure the app has write permissions in its directory
3. **Invalid JSON**: Check the configuration file syntax if you edit it manually
4. **Missing departments**: Departments must exist in configuration to be accessible

### Error Messages

- "Invalid department": Department doesn't exist in configuration
- "Process and employee name are required": Form validation failed
- "Employee already exists": Duplicate employee names not allowed in same process
- "Passwords do not match": Password confirmation failed
- "Password must be at least 6 characters": Password too short

## Future Enhancements

Potential improvements to consider:
- Bulk import/export of employee data
- Department templates for quick setup
- Audit logging of changes
- Role-based permissions within departments
- Integration with HR systems
- Employee scheduling preferences