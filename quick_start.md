# Quick Start Guide for VS Code

## 🚀 Getting Started in 3 Steps

### 1. Open in VS Code
- **Option A**: Open VS Code → File → Open Workspace → Select `rota_app.code-workspace`
- **Option B**: Right-click on project folder → "Open with Code"

### 2. Install Dependencies
Open VS Code terminal (`Ctrl + Shift + ``) and run:
```bash
pip install -r requirements.txt
```

### 3. Run the Application
- **Method 1**: Press `F5` (uses VS Code debugger)
- **Method 2**: Run in terminal: `python app.py`
- **Method 3**: Double-click `start_server.bat` (Windows)

The app will start at `http://localhost:5000`

## 🎯 VS Code Features Configured

### Debugging
- **F5**: Start with debugger attached
- **Breakpoints**: Click left margin to set breakpoints
- **Variables**: View variables in debug panel
- **Call Stack**: See execution flow

### Extensions Recommended
VS Code will suggest installing:
- **Python**: Main Python support
- **Jinja**: Template syntax highlighting
- **Auto Rename Tag**: HTML tag pair editing
- **Flake8**: Python linting

### File Structure
```
rota_app/
├── 📄 app.py                    ← Main Flask app (start here)
├── 📁 templates/               ← HTML templates
│   ├── base.html               ← Main layout
│   ├── index.html              ← Home page
│   ├── dept.html               ← Department rota
│   └── department_settings.html ← Admin settings
├── 📁 static/                  ← Static files (CSS, images)
├── 📁 data/                    ← JSON data files
└── 📄 README.md                ← Full documentation
```

## 🔧 Development Tips

### Editing Templates
- Templates use **Jinja2** syntax
- VS Code will highlight `{{ variables }}` and `{% blocks %}`
- Auto-completion for HTML + Jinja

### Python Development  
- **IntelliSense**: Auto-completion for Flask
- **Linting**: Automatic code quality checks
- **Formatting**: Code formats on save (Black formatter)

### Live Reloading
- Flask debug mode is enabled
- Changes to Python files auto-restart server
- Refresh browser to see template changes

## 🎨 Customization

### Change Styling
Edit the `<style>` sections in templates:
- `base.html`: Global styles
- `dept.html`: Rota page styles
- `index.html`: Home page styles

### Add New Features
1. Add route in `app.py`
2. Create template in `templates/`
3. Test with `F5` debugger

### Modify Departments
Edit the `DEPARTMENTS` dictionary in `app.py` around line 26

## 🐛 Troubleshooting in VS Code

### Common Issues
1. **Python not found**: Select Python interpreter (Ctrl+Shift+P → "Python: Select Interpreter")
2. **Modules not found**: Ensure you ran `pip install -r requirements.txt`
3. **Port in use**: Check terminal for port conflicts
4. **Templates not loading**: Verify working directory is project root

### Debug Console
Use the debug console (when debugging) to:
- Check variable values
- Test Flask routes
- Inspect request data

### Terminal Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run with debug
python app.py

# Check Python version
python --version

# List installed packages
pip list
```

---

**🎉 You're ready to develop! Open `app.py` and press F5 to start.**