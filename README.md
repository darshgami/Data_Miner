# Data Scraping Project

This project is a data scraping application built with Django, featuring a web scraper and a browser extension.

## Features

- Django backend for data management
- Web scraper for collecting data from sources like IndiaMart
- Browser extension for enhanced scraping capabilities

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd Data_Scraping
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Start the Django server:
   ```
   python manage.py runserver
   ```

## Usage

- Run the scraper: `python test_scrape.py`
- Access the API at `http://localhost:8000`

## Browser Extension

Navigate to the `extension/` directory and follow the extension's README for setup instructions.

## Contributing

Please read the contributing guidelines before making contributions.

## License

This project is licensed under the MIT License.