# Payment Management System

A Flask-based web application for managing payments, generating checks, and handling payment records with MySQL database integration.

## Features

- Add, edit, view, and delete payment records
- Generate and download payment checks as PDF
- Search and filter payment records
- RESTful API endpoints for payment data
- Secure database operations
- Responsive web interface

## Prerequisites

- Python 3.8 or higher
- MySQL Database
- Git (for version control)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd payment-management-system
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```
host=your_mysql_host
database=your_database_name
user=your_database_user
password=your_database_password
```

## Local Development

```bash
python app.py
```
This will create the necessary database tables automatically.


The application will be available at `http://127.0.0.1:5000`

## Deploying to Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy the application:
```bash
vercel
```

4. Configure environment variables in Vercel:
   - Go to your project settings in the Vercel dashboard
   - Navigate to the "Environment Variables" section
   - Add the following variables:
     - `host`: Your MySQL host
     - `database`: Your database name
     - `user`: Your database user
     - `password`: Your database password

5. The project is already configured for Vercel deployment with:
   - `vercel.json` for build and route configurations
   - Python runtime configuration
   - Flask production settings

6. For production deployment:
```bash
vercel --prod
```

## Project Structure

```
.
├── app.py              # Main Flask application
├── checkprinting.py    # PDF generation logic
├── requirements.txt    # Project dependencies
├── templates/         # HTML templates
│   ├── add_payment.html
│   ├── base.html
│   ├── edit_payment.html
│   ├── home.html
│   └── view_payments.html
└── vercel.json        # Vercel deployment configuration
```

## Environment Variables

- `host`: MySQL database host
- `database`: Database name
- `user`: Database username
- `password`: Database password

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.