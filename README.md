# Flask Online Store README

This is a Flask-based online store application designed to handle both user and seller functionalities. It provides features for user registration, login, browsing items, adding items to the cart, checkout, and seller-specific operations like adding and managing products.

## Table of Contents
- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

## Features

### User Features
- User registration with email, name, and password
- User login and logout
- View available items
- Add items to the cart
- Remove items from the cart
- View and manage addresses
- Checkout and payment

### Seller Features
- Seller registration with email, name, password, phone number, and address
- Seller login and logout
- Add new items for sale
- View and manage their listed items
- Delete items from their inventory
- View orders placed for their items

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/your_username/flask-online-store.git
   ```
2. Navigate to the project directory:
   ```
   cd flask-online-store
   ```
3. Create a virtual environment:
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```
5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
6. Set up the database:
   - Execute the following command in your terminal:
     ```
     python main.py
     ```
   - This will create the necessary SQLite database file `store.db`.

## Usage

1. Start the Flask application:
   ```
   python main.py
   ```
2. Access the application in your web browser at `http://127.0.0.1:5000/`.
3. Navigate through the provided user and seller functionalities using the web interface.

## File Structure

- `main.py`: The main Flask application file containing route definitions and database models.
- `form.py`: Contains form definitions using Flask-WTF for user input validation.
- `upload_to_firebase.py`: Utility module for uploading images to Firebase.
- `templates/`: Directory containing HTML templates for the frontend.
- `static/`: Directory containing static files such as CSS stylesheets, JavaScript, and images.

## Dependencies

- Flask: Micro web framework for Python.
- Flask-SQLAlchemy: Flask extension for SQLAlchemy ORM integration.
- Flask-Login: Flask extension for user session management.
- Flask-Bootstrap: Flask extension for integrating Bootstrap CSS framework.
- Werkzeug: WSGI utility library for Python.
- WTForms: Library for building web forms in Flask applications.
- SQLAlchemy: SQL toolkit and Object-Relational Mapping (ORM) library for Python.

## Contributing

Contributions are welcome! Feel free to open issues or pull requests for any enhancements or bug fixes.
