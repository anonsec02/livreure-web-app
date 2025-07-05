# Livreure Web App

This repository contains the source code for the Livreure web application, a comprehensive delivery platform designed for the Mauritanian market. The application aims to provide fast, reliable, and efficient delivery services for food, groceries, and other essential items.

## Features

- **Modern and Responsive UI/UX**: A user-friendly interface with full Arabic language support and RTL (Right-to-Left) text direction, optimized for various devices.
- **Enhanced Backend System**: Robust backend with improved authentication (JWT), new API endpoints for various services, and real-time order tracking.
- **Livreure Plus Subscription**: A premium subscription service offering exclusive benefits like free delivery and discounts.
- **Comprehensive Authentication**: Secure authentication system for customers, restaurants, and delivery agents.
- **Advanced Search and Filtering**: Easily find restaurants and stores with advanced search and filtering options.
- **Mobile Compatibility**: Designed with a mobile-first approach and touch support for seamless experience on smartphones.

## Project Structure

- `backend/`: Contains the Flask backend application, including API routes, database models, and business logic.
- `index.html`: The main frontend HTML file, enhanced with modern UI/UX.
- `styles.css`: CSS file for styling the frontend, with a focus on Mauritanian cultural elements and modern design principles.
- `script.js`: JavaScript file for frontend interactivity and dynamic features.
- `test_api.py`: A comprehensive Python script for testing various API endpoints.
- `deployment-guide.md`: A guide for deploying the Livreure web application.
- `livreure-development-summary.md`: A detailed summary of the development process and implemented features.
- `delivery_platform_research.md`: Research findings on global delivery platforms that inspired the improvements.

## Setup and Installation

### Backend Setup

1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your database connection in the `.env` file:
   ```
   DATABASE_URL="mysql+pymysql://<user>:<password>@<host>:<port>/<database_name>"
   SECRET_KEY="your_secret_key_here"
   ```
4. Run the Flask application to initialize the database (if not already done):
   ```bash
   python src/main.py
   ```

### Frontend Setup

No specific setup is required for the frontend as it's a static web application. Simply open `index.html` in your browser or deploy it to a web server.

## API Endpoints

The backend exposes various API endpoints for different functionalities. Refer to the `backend/src/routes/` directory for detailed API definitions.

## Contributing

Contributions are welcome! Please feel free to fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.


