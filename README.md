# Libya-TradeNet

Libya TradeNet is a web-based platform for managing and monitoring trade operations in Libya. It supports import workflows, document management, and role-based access for different stakeholders. The system also uses machine learning to detect anomalies and assess risk in trade transactions.

## Setup Instructions

### 1. Configure Python Interpreter

**Using PyCharm:**
1. Open Settings/Preferences → Project: Libya-TradeNet → Python Interpreter
2. Click the gear icon → Add
3. Select "Virtualenv Environment"
4. Choose "Existing environment"
5. Navigate to: `C:\Users\Malek\PycharmProjects\Libya-TradeNet\venv\Scripts\python.exe`
6. Click OK

**Using Command Line:**
```bash
# Activate virtual environment
venv\Scripts\activate

# Verify Django installation
python -m django --version
```

### 2. Run the Development Server

```bash
# Using virtual environment
venv\Scripts\python.exe manage.py runserver

# Or after activation
python manage.py runserver
```

### 3. Access the Application

- **Main App**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Project Structure

- `libya_tradenet/` - Main Django project
- `trade_management/` - Trade operations app
- `venv/` - Virtual environment
- `requirements.txt` - Project dependencies
- `manage.py` - Django management script
