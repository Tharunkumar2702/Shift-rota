# Create Complete Rota App Package for VS Code Testing
Write-Host "Creating Shift Rota App Package..." -ForegroundColor Green

# Define package name and paths
$PackageName = "ShiftRotaApp_Complete"
$PackageDir = "..\$PackageName"
$ZipFile = "..\$PackageName.zip"

# Remove existing package if it exists
if (Test-Path $PackageDir) {
    Remove-Item $PackageDir -Recurse -Force
}
if (Test-Path $ZipFile) {
    Remove-Item $ZipFile -Force
}

# Create package directory
New-Item -ItemType Directory -Path $PackageDir -Force | Out-Null

Write-Host "Copying files..." -ForegroundColor Yellow

# Copy all necessary files and folders
$ItemsToCopy = @(
    "app.py",
    "requirements.txt",
    "start_server.bat",
    "README.md",
    "quick_start.md",
    "rota_app.code-workspace",
    "templates",
    "static",
    "data"
)

foreach ($Item in $ItemsToCopy) {
    if (Test-Path $Item) {
        if ((Get-Item $Item).PSIsContainer) {
            # Copy directory
            Copy-Item $Item -Destination $PackageDir -Recurse -Force
            Write-Host "  ✓ Copied folder: $Item" -ForegroundColor Cyan
        } else {
            # Copy file
            Copy-Item $Item -Destination $PackageDir -Force
            Write-Host "  ✓ Copied file: $Item" -ForegroundColor Cyan
        }
    } else {
        Write-Host "  ⚠ Missing: $Item" -ForegroundColor Red
    }
}

# Create additional VS Code files
Write-Host "Creating VS Code configuration..." -ForegroundColor Yellow

# Create .vscode directory
New-Item -ItemType Directory -Path "$PackageDir\.vscode" -Force | Out-Null

# Create launch.json for VS Code debugging
$LaunchJson = @"
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run Flask App",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/app.py",
            "console": "integratedTerminal",
            "env": {
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "1"
            },
            "jinja": true,
            "cwd": "${workspaceFolder}"
        }
    ]
}
"@

Set-Content -Path "$PackageDir\.vscode\launch.json" -Value $LaunchJson

# Create settings.json for VS Code
$SettingsJson = @"
{
    "python.defaultInterpreterPath": "python",
    "python.terminal.activateEnvironment": true,
    "files.associations": {
        "*.html": "html"
    },
    "emmet.includeLanguages": {
        "jinja-html": "html"
    },
    "files.exclude": {
        "__pycache__": true,
        "*.pyc": true
    }
}
"@

Set-Content -Path "$PackageDir\.vscode\settings.json" -Value $SettingsJson

Write-Host "  ✓ Created VS Code configuration" -ForegroundColor Cyan

# Create a comprehensive setup guide
$SetupGuide = @"
# 🚀 Shift Rota App - VS Code Setup Guide

## Quick Start (3 Steps)

### 1. Open in VS Code
- Open VS Code
- File → Open Folder → Select this folder (`$PackageName`)
- Or double-click `rota_app.code-workspace`

### 2. Install Dependencies
Open terminal in VS Code (`Ctrl + Shift + ` `) and run:
```bash
pip install -r requirements.txt
```

### 3. Run the App
- **Method 1**: Press `F5` (recommended - includes debugger)
- **Method 2**: Terminal: `python app.py`
- **Method 3**: Double-click `start_server.bat`

## 🌐 Access the App
Open browser to: **http://localhost:5000**

## 🔑 Default Login Credentials

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
- **Password**: `editor123`

## 🎯 How to Test

### 1. Employee Access (Read-Only)
1. Go to home page
2. Click any department
3. Choose "👥 Employee Login"
4. View rota without editing

### 2. Admin Access (Full Edit)
1. Go to home page  
2. Click any department
3. Choose "🔑 Admin Login"
4. Enter department password
5. Edit shifts and see colors change instantly
6. Access Settings via top menu

## 🛠️ VS Code Features Ready

### Debugging
- **F5**: Start with breakpoints
- **F9**: Toggle breakpoint
- **F10**: Step over
- **F11**: Step into

### File Structure
```
$PackageName/
├── app.py                     ← Main Flask app
├── templates/                 ← HTML templates
├── static/                    ← CSS, images
├── data/                      ← JSON data files
├── .vscode/                   ← VS Code config
└── README.md                  ← Full documentation
```

## 🚨 Troubleshooting

### Common Issues
1. **Python not found**: Select interpreter (Ctrl+Shift+P → "Python: Select Interpreter")
2. **Port in use**: Change port in app.py or kill process on port 5000
3. **Module errors**: Run `pip install -r requirements.txt`

### Need Help?
- Check README.md for full documentation
- Check browser console for JavaScript errors
- Check VS Code terminal for Python errors

---
**🎉 Happy Testing! The app is ready to run.**
"@

Set-Content -Path "$PackageDir\SETUP_GUIDE.md" -Value $SetupGuide

# Create the ZIP file
Write-Host "Creating ZIP package..." -ForegroundColor Yellow
try {
    Compress-Archive -Path $PackageDir -DestinationPath $ZipFile -Force
    Write-Host "✅ Package created successfully!" -ForegroundColor Green
    Write-Host "📦 Location: $ZipFile" -ForegroundColor Cyan
    Write-Host "📁 Folder: $PackageDir" -ForegroundColor Cyan
    
    # Show file size
    $ZipSize = (Get-Item $ZipFile).Length / 1MB
    Write-Host "📊 Size: $([math]::Round($ZipSize, 2)) MB" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Error creating ZIP: $_" -ForegroundColor Red
}

Write-Host "`n🚀 Ready to test!" -ForegroundColor Green
Write-Host "1. Extract $ZipFile" -ForegroundColor White
Write-Host "2. Open folder in VS Code" -ForegroundColor White  
Write-Host "3. Press F5 to run with debugger" -ForegroundColor White
Write-Host "4. Go to http://localhost:5000" -ForegroundColor White