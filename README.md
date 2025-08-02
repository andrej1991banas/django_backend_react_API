# Project Name
A full-stack web application built with Django REST Framework backend and React frontend, featuring JWT authentication and modern state management.

# Production

**https://subtle-rabanadas-b5cc2b.netlify.app**
#  Tech Stack 🚀

## Backend

**Django REST Framework** - RESTful API development
**JWT Authentication** - Secure token-based authentication with SimpleJWT
**PostgreSQL** - Primary database
**AWS S3** - File storage via django-storages and boto3
**Stripe** - Payment processing integration
**Email** - Django Anymail for email services
**API Documentation** - Auto-generated with drf-yasg (Swagger/OpenAPI)

Frontend

**React 18** - Modern React with hooks
**Zustand** - Lightweight state management
**Vite** - Fast build tool and dev server
**Yarn** - Package manager
**React Router** - Client-side routing
**Axios** - HTTP client for API calls
**Chart.js** - Data visualization
**CKEditor 5** - Rich text editing
**PayPal SDK** - Payment integration
**SweetAlert2** - Beautiful alerts and modals

# 📋 Prerequisites

Python 3.8+
Node.js 16+
Yarn package manager
PostgreSQL database
AWS S3 bucket (for file storage)

# Backend Setup

**1. Clone the repository**
```bash
git clone <repository-url>
cd <project-directory>
```

**2.Create Virtul Enviroment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3.Install Python dependencies**
```bash
pip install -r requirements.txt
```

**4.Environment Configuration**
Create a .env file in the root directory:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-s3-bucket
AWS_S3_REGION_NAME=your-region

# Email Configuration
ANYMAIL_API_KEY=your-email-service-api-key

# Stripe Configuration
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
```

**5.Database Migration**

```bash
python manage.py makemigrations
python manage.py migrate
```
**6.Create SuperUser**

```bash
python manage.py createsuperuser
```

**7.Run Backend Server**

```bash
python manage.py runserver
```

# Frontend Setup

**1.Navigate to frontend directory**

```bash
cd frontend
```

**2.Install dependencies**
```bash
yarn install
```
**3.Start development server**
```bash
yarn dev
```

# 🔧 Development

**Backend Development**

API endpoints are available at http://localhost:8000/api/
Admin panel: http://localhost:8000/admin/
API documentation: http://localhost:8000/swagger/ or http://localhost:8000/redoc/

**Frontend Development**

Development server: http://localhost:5173/ (Vite default)
Hot reload enabled for rapid development

**Authentication Flow**
The application uses JWT tokens for authentication:

- Login returns access and refresh tokens
- Access tokens are short-lived and used for API requests
- Refresh tokens are used to obtain new access tokens
- Tokens are managed by Zustand store on the frontend

# 🚀 Deployment
**Backend Deployment**

Configured for deployment with Gunicorn WSGI server
Environment variables should be set in production
Database migrations need to be run: python manage.py migrate
Static files collection: python manage.py collectstatic

# Frontend Deployment

```bash
cd frontend
yarn build
```

# 📝 Available Scripts
**Backend**

- python manage.py runserver - Start development server
- python manage.py makemigrations - Create database migrations
- python manage.py migrate - Apply database migrations
- python manage.py collectstatic - Collect static files
- python manage.py test - Run tests

**Frontend**

- yarn dev - Start development server
- yarn build - Build for production
- yarn preview - Preview production build
- yarn lint - Run ESLint

# 🔑 Key Features

- JWT-based authentication system
- File upload and storage with AWS S3
- Payment processing with Stripe and PayPal
- Rich text editing capabilities
- Data visualization with charts
- Responsive design
- API documentation
- Admin interface

# 🤝 Contributing
- Fork the repository
- Create a feature branch (git checkout -b feature/AmazingFeature)
- Commit your changes (git commit -m 'Add some AmazingFeature')
- Push to the branch (git push origin feature/AmazingFeature)
- Open a Pull Request

# 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
Autho **Andrej Banas**
