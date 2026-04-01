# Libya TradeNet Dashboard

## Overview
This is a complete, self-contained dashboard package for Libya TradeNet project. It includes all necessary templates, static files, and components for a modern Arabic dashboard interface.

## Features
- **Modern Arabic Interface**: RTL layout with Almarai font family
- **Bootstrap 5**: Responsive design with modern UI components
- **Dashboard Analytics**: KPI cards, charts, and data visualization
- **Interactive Sidebar**: Navigation menu with collapsible sections
- **Chart.js Integration**: Revenue charts with period filtering
- **Message System**: Django messages integration
- **Profile Management**: User profile dropdown

## File Structure
```
libya_trade_dashboard/
├── templates/
│   ├── base.html              # Main template with layout
│   ├── dashboard.html          # Dashboard page
│   ├── parts/
│   │   ├── header.html         # Top navigation bar
│   │   ├── sidebar.html       # Side navigation menu
│   │   ├── footer.html         # Footer
│   │   ├── title.html          # Page title component
│   │   └── head.html           # Arabic fonts and styles
│   └── components/
│       ├── messages.html      # Django messages
│       └── buttons.html        # Dynamic buttons
└── static/
    ├── css/
    │   └── style.css            # Main stylesheet
    ├── js/
    │   ├── custom.min.js        # Custom JavaScript
    │   └── dlabnav-init.js      # Navigation initialization
    ├── vendor/                 # Third-party libraries
    ├── icons/                   # Font icons (FontAwesome, etc.)
    ├── fonts/                   # Arabic fonts (Almarai)
    └── images/                  # Images and assets
```

## Installation

### 1. Copy Files to Your Project
Copy the entire `libya_trade_dashboard` folder to your Django project root.

### 2. Update Django Settings
Add these to your `settings.py`:

```python
# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'libya_trade_dashboard/static'),
]

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'libya_trade_dashboard/templates'),
        ],
        'APP_DIRS': True,
        # ... rest of config
    },
]
```

### 3. Create Dashboard View
Add this to your `views.py`:

```python
from django.shortcuts import render

@login_required
def dashboard(request):
    context = {
        'total_orders': 100,
        'total_revenue': 15000.50,
        'total_items': 250,
        'total_profit': 5000.75,
        'period': 'day',
        'start': None,
        'end': None,
        'top_products': [],
        'chart_labels': '["Jan", "Feb", "Mar", "Apr", "May"]',
        'chart_data': '[1000, 1500, 1200, 1800, 2000]',
    }
    return render(request, 'dashboard.html', context)
```

### 4. Add URL Route
Add this to your `urls.py`:

```python
path('dashboard/', views.dashboard, name='dashboard'),
```

## Customization

### Update Sidebar Navigation
Edit `templates/parts/sidebar.html` to match your project's URLs and menu structure.

### Update Branding
- Replace logo in `templates/parts/header.html`
- Update footer in `templates/parts/footer.html`
- Modify page title in `templates/base.html`

### Customize Colors
Edit `static/css/style.css` to change the primary colors and styling.

## Dependencies
- Django 3.2+
- Bootstrap 5 (included)
- jQuery (included)
- Chart.js 3.9.1 (CDN)
- FontAwesome icons (included)

## Features Included

### Dashboard Components
- **KPI Cards**: Total Orders, Revenue, Items Sold, Profit
- **Revenue Chart**: Line chart with period filtering (Daily/Monthly/Yearly)
- **Top Products Table**: Best-selling products display
- **Responsive Design**: Works on desktop and mobile devices

### Navigation
- **Header**: Logo, notifications, user profile dropdown
- **Sidebar**: Collapsible menu with icons
- **Footer**: Copyright information

### UI Components
- **Messages**: Django flash messages with alerts
- **Buttons**: Dynamic button component
- **Forms**: Styled form elements with validation
- **Tables**: Responsive data tables

## Browser Support
- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## License
This dashboard package is provided as-is for use in Libya TradeNet project.
