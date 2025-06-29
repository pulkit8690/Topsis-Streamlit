# Topsis Streamlit

## Overview
Topsis Streamlit is a web application that implements the TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) decision-making method. The application allows users to upload datasets, specify weights and impacts, and receive ranked results based on their inputs.

## Project Structure
```
topsis-streamlit
├── app.py                  # Main entry point of the application
├── config.py               # Configuration settings for the application
├── models                  # Database models
│   ├── __init__.py
│   └── user.py             # User model definition
├── routes                  # Application routes
│   ├── __init__.py
│   ├── auth.py             # Authentication routes (signup, login, OTP verification)
│   └── topsis.py           # TOPSIS-related routes (dataset submission, processing)
├── services                # Business logic and services
│   ├── __init__.py
│   ├── email_service.py     # Functions for sending emails
│   └── topsis_service.py     # Functions for processing datasets and calculating scores
├── utils                   # Utility functions
│   ├── __init__.py
│   ├── file_helpers.py      # File operation helpers
│   └── validators.py        # Validation functions
├── templates               # HTML templates for rendering views
│   ├── index.html
│   ├── login.html
│   ├── result.html
│   ├── signup.html
│   ├── verify_otp.html
│   └── weights_impacts.html
├── uploads                 # Directory for uploaded files
│   └── .gitkeep
├── static                  # Static files (CSS, JS)
│   ├── css
│   └── js
├── .env.example            # Example environment variables
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/topsis-streamlit.git
   cd topsis-streamlit
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables by copying `.env.example` to `.env` and filling in the necessary values.

## Usage
1. Run the application:
   ```
   python app.py
   ```

2. Open your web browser and navigate to `http://127.0.0.1:5000`.

3. Use the application to sign up, log in, upload datasets, and process TOPSIS results.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.