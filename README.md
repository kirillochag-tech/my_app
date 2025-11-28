# Employee Feedback Management System

This Django application facilitates interaction with remote employees, collecting and visualizing feedback. It supports three user roles: Super Moderator, Moderator, and Employee, each with specific permissions and interfaces.

## Features

- **Role-based Access Control**: Three distinct user roles with different permissions
- **Task Management**: Create, assign, and track various task types
- **Web Interface**: Separate interfaces for employees and moderators
- **Feedback Visualization**: Statistics and results display
- **File Upload**: Support for photo uploads with quality checking
- **Excel Integration**: Import/export of data from/to Excel files
- **Client Management**: Grouping and assignment of clients to employees
- **Password Policy**: Minimum 4-character password requirement for moderators and employees

## Requirements

- Python 3.8+
- Django 4.2+
- Additional packages (install via requirements.txt)

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
6. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
employee_feedback/
├── manage.py
├── requirements.txt
├── README.md
├── employee_feedback/          # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                  # User authentication and roles
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── admin.py
├── tasks/                     # Task management
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── admin.py
├── clients/                   # Client management
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── admin.py
├── feedback/                  # Feedback and results
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── admin.py
├── groups/                    # Employee groups
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── admin.py
└── static/                    # Static files
    ├── css/
    ├── js/
    └── images/
```