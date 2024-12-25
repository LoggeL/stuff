# Theater Inventory Management System

A web-based inventory management system designed specifically for theaters to track costumes, props, sets, and other theatrical items.

## Features

- **Item Management**
  - Create, view, edit, and delete inventory items
  - Categorize items by type (costumes, props, sets, etc.)
  - Assign items to specific locations
  - Add custom properties for each item type
  - Upload and manage images and files for each item
  - Advanced filtering and search capabilities

- **File Management**
  - Upload images and files for each item
  - Automatic image preview generation
  - Support for multiple file types (images, PDFs, documents)
  - Files are stored in a structured directory system
  - Secure file handling with sanitized filenames

- **Location Management**
  - Track where items are stored
  - Organize items by location
  - Easy location assignment and updates

- **User Management**
  - Role-based access control
  - Secure authentication using JWT
  - Different permission levels for viewing and editing

- **Property System**
  - Define custom properties for each item type
  - Support for different property types:
    - Text
    - Numbers
    - Dates
    - Boolean (Yes/No)
  - Required/optional property settings
  - Property-based filtering

## Technical Details

### Backend (Python/Flask)
- RESTful API built with Flask
- SQLite database with SQLAlchemy ORM
- JWT authentication
- File storage in `/static/pictures/` directory
- Structured file organization by item type and ID
- Configurable host and port through environment variables

### Frontend (Vue.js)
- Modern, responsive UI built with Vue 3
- Bootstrap 5 for styling
- Dynamic form handling
- Real-time image preview
- Advanced filtering system
- File upload with progress tracking
- Configurable backend URL through environment variables

## Project Structure

```
├── frontend/              # Vue.js frontend application
│   ├── src/
│   │   ├── views/        # Vue components for each page
│   │   ├── components/   # Reusable Vue components
│   │   ├── router/       # Vue Router configuration
│   │   └── main.js       # Vue application entry point
│   └── package.json      # Frontend dependencies
├── src/                  # Flask backend application
│   ├── app.py           # Main Flask application
│   ├── models.py        # Database models
│   └── inventory.db     # SQLite database
├── static/              # Static files
│   ├── pictures/        # Uploaded files storage
│   └── uploads/         # Item-specific files
└── README.md            # Project documentation
```

## Configuration

### Backend Configuration
Copy `src/.env.example` to `src/.env` and adjust the values:
```bash
# Flask server configuration
FLASK_PORT=5000                  # Port for the Flask server
FLASK_HOST=127.0.0.1            # Host for the Flask server (use 0.0.0.0 to allow external access)

# Security
JWT_SECRET_KEY=change-me-in-production   # Secret key for JWT token generation

# File upload configuration
MAX_CONTENT_LENGTH=16777216      # Maximum file size in bytes (16MB)
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif,pdf,doc,docx  # Allowed file extensions

# Database
SQLALCHEMY_DATABASE_URI=sqlite:///inventory.db  # Database connection string
```

### Frontend Configuration
Copy `frontend/.env.example` to `frontend/.env` and adjust the values:
```bash
# Backend server URL
VITE_BACKEND_URL=http://127.0.0.1:5000  # URL of the backend server

# Development server configuration
VITE_PORT=5173                          # Port for the Vite development server
VITE_HOST=127.0.0.1                     # Host for the Vite development server

# Build configuration
VITE_BASE_URL=/                         # Base URL for production build
```

## Installation

1. Clone the repository

2. Set up the backend:
   ```bash
   cd src
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   # Create .env file with your configuration
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   pnpm install
   # Create .env file with your configuration
   ```

## Running the Application

1. Start the backend server (will use ports from .env):
   ```bash
   cd src
   python app.py
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   pnpm dev
   ```

3. Access the application at the configured URL (default: http://localhost:5173)

## File Storage

Files are stored in the following structure:
```
static/
└── pictures/
    └── items/
        ├── costumes/
        │   └── [item_id]/
        │       └── [files]
        ├── props/
        │   └── [item_id]/
        │       └── [files]
        └── sets/
            └── [item_id]/
                └── [files]
```

## Security Considerations

- All filenames are sanitized before storage
- File types are restricted to allowed extensions
- File size is limited to prevent abuse
- JWT authentication required for all operations
- Role-based access control for sensitive operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
