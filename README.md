# Data Scraping & Cleaning Pipeline

A comprehensive Django-based data cleaning, validation, and standardization system for company information. Automatically cleans messy datasets and exports Excel-ready clean data.

## ✓ What's Included

This project provides a **complete end-to-end solution** for:

### 1. **Data Cleaning & Validation**
- Remove exact and fuzzy duplicate records
- Standardize company names (capitalization, spacing, consistency)
- Validate and sanitize emails (reject fake domains)
- Convert phone numbers to international format
- Fix and validate URLs (ensure proper protocol)
- Clean and consolidate addresses
- Assess data quality (Complete/Incomplete/Suspicious)

### 2. **Data Generation**
- Generate realistic messy test data with various real-world issues
- Includes duplicates, fake emails, invalid phone numbers, partial URLs
- Simulates misaligned data and fragmented addresses

### 3. **Web Scraping** (Ready to integrate)
- Base scraper module for extracting business data
- Support for multiple business directories
- Email extraction and phone number parsing

### 4. **Excel Export**
- Formatted Excel files with headers and proper column widths
- Quality status column (Complete/Incomplete/Suspicious)
- Summary statistics and data quality reporting
- CSV export as alternative format

### 5. **REST API**
- Django REST endpoints for all operations
- Full pipeline automation (scrape → clean → export)
- Batch processing capabilities

---

## 📋 Dataset Requirements

The system expects data with these columns:
- **Company Name** - Business/company name
- **Email** - Company email address
- **Phone No** - Contact phone number
- **URL** - Company website
- **Address** - Physical address

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the Demo

```bash
python demo.py
```

This demonstrates:
- Generating 30 realistic messy records
- Cleaning and deduplicating
- Exporting to Excel and CSV
- Data quality statistics
- Before/after comparisons

### 3. Start Django Server

```bash
python manage.py runserver
```

---

## 📡 API Endpoints

### Generate Test Data
```bash
POST /api/test-data/
Content-Type: application/json

{
  "count": 50,
  "include_fakes": true,
  "include_duplicates": true,
  "include_shifted": true
}
```

### Clean Data
```bash
POST /api/clean/
Content-Type: application/json

{
  "records": [
    {
      "Company Name": "Acme Corp",
      "Email": "info@acme.com",
      "Phone No": "9876543210",
      "URL": "www.acme.com",
      "Address": "123 Main St"
    }
  ],
  "remove_duplicates": true
}
```

### Export to Excel
```bash
POST /api/export/
Content-Type: application/json

{
  "records": [...],
  "filename": "companies.xlsx"
}
```

### Full Pipeline
```bash
POST /api/pipeline/
Content-Type: application/json

{
  "source": "test",  // or "scrape", "upload"
  "count": 100,
  "city": "Mumbai",
  "export_format": "excel"  // or "csv"
}
```

---

## 🔧 Cleaning Features

### Email Validation
- ✓ Rejects fake domains: test@test.com, example@example.com, etc.
- ✓ Validates format compliance
- ✓ Removes test patterns (test@, admin@, noreply@)
- ✓ Standardizes to lowercase

### Phone Standardization
- ✓ Converts to international format: +919876543210
- ✓ Handles multiple formats (with dashes, brackets, spaces)
- ✓ Validates length (8-15 digits)
- ✓ Removes invalid patterns

### URL Fixing
- ✓ Ensures protocol: https://
- ✓ Fixes missing protocols
- ✓ Validates URL structure
- ✓ Removes extra whitespace

### Deduplication
- ✓ Case-insensitive matching
- ✓ Handles company name variations
- ✓ Merges records keeping most complete data
- ✓ Preserves primary information

### Data Quality Assessment
- **Complete** - All key fields present and valid ✓
- **Incomplete** - Missing some important fields ⚠
- **Suspicious** - Invalid data or inconsistent values ✗

---

## 📊 Example Workflow

### Input (Messy Data)
```
Company Name    : Tata Steel  Ltd 
Email           :   INFO@EXAMPLE.COM  
Phone No        : 9876543210
URL             : www.company.com
Address         : Plot 123 | Mumbai
```

### Output (Cleaned Data)
```
Company Name    : Tata Steel Ltd
Email           : (removed - fake domain)
Phone No        : +919876543210
URL             : https://www.company.com
Address         : Plot 123 Mumbai
Status          : Incomplete
```

---

## 📁 Project Structure

```
Data_Scraping/
├── api/
│   ├── data_cleaner.py          # Main cleaning logic
│   ├── test_data_generator.py   # Generates messy test data
│   ├── scraper.py               # Web scraping module
│   ├── views.py                 # REST API views
│   ├── urls.py                  # API routing
│   ├── models.py                # Database models
│   └── tests.py
├── backend/
│   ├── settings.py
│   ├── urls.py
│   ├── requirements.txt
│   └── wsgi.py
├── extension/                   # Chrome extension (optional)
├── manage.py                    # Django management
├── demo.py                      # Live demonstration script
├── exports/                     # Generated Excel/CSV files
└── README.md
```

---

## 💾 Data Processing Details

### Step 1: Input
- Upload CSV/Excel or scrape from web
- Accept any data format with Company Name, Email, Phone, URL, Address

### Step 2: Duplicate Detection
- Create normalized key from company name (lowercase, remove punctuation)
- Group records with same key
- Merge duplicate records keeping most complete information

### Step 3: Validation & Standardization
- **Email**: Validate format, reject fakes, remove test patterns
- **Phone**: Convert to international format (+91XXXXXXXXXX)
- **URL**: Ensure proper protocol, fix common issues
- **Address**: Remove junk characters, consolidate fragments
- **Company Name**: Standardize capitalization, remove extra spaces

### Step 4: Quality Assessment
- Count valid key fields
- Assign quality status (Complete/Incomplete/Suspicious)
- Flag any invalid data

### Step 5: Export
- Format into Excel with headers
- Set proper column widths
- Freeze header row
- Generate CSV backup
- Include summary statistics

---

## 🎯 Key Rules & Standards

### Do NOT
- ✗ Duplicate companies
- ✗ Invent information
- ✗ Guess missing values
- ✗ Keep test/fake data

### DO
- ✓ Prefer accuracy over completeness
- ✓ Merge most complete records
- ✓ Standardize formats consistently
- ✓ Flag suspicious data clearly
- ✓ Keep output Excel-ready

---

## 🧪 Testing

Run the demonstration to see all features:

```bash
python demo.py
```

This will:
1. Generate 30 realistic messy records with various issues
2. Clean and deduplicate them
3. Show before/after comparisons
4. Export to Excel and CSV
5. Display data quality statistics
6. Show validation examples

Check the `exports/` folder for generated files.

---

## 📦 Output Format

### Excel File Columns
| Column | Format | Validation |
|--------|--------|-----------|
| Company Name | Title Case | Non-empty |
| Email | lowercase | Valid format, no fakes |
| Phone No | +91XXXXXXXXXX | 8-15 digits, valid |
| URL | https://... | Complete protocol |
| Address | Readable text | Cleaned, consolidated |
| Status | Text | Complete/Incomplete/Suspicious |

### Data Quality Flags
```
Complete   - All fields present and valid (✓)
Incomplete - Missing important fields (⚠)
Suspicious - Invalid data or inconsistencies (✗)
```

---

## 🚀 Next Steps

1. **Customize**: Modify scraper targets in `api/scraper.py`
2. **Deploy**: Configure Django settings for production
3. **Integrate**: Add your own data sources
4. **Extend**: Add more validation rules as needed
5. **Monitor**: Track data quality metrics

---

## 📝 Configuration

Edit `api/data_cleaner.py` to customize:
- Email domain blacklist (FAKE_EMAIL_DOMAINS)
- Phone country codes (default: +91 for India)
- Validation regex patterns
- Quality assessment thresholds

---

## ⚠️ Important Notes

- **Accuracy First**: Clean data is more valuable than complete data
- **No Guessing**: Missing values are better than guessed ones
- **Consistency**: Apply same rules to all records
- **Quality Matters**: Use Status field to track data reliability

---

## 📞 Support

For issues or questions:
1. Check `exports/` folder for generated files
2. Review the demo output with examples
3. Check data quality statistics
4. Inspect suspicious records manually

---

## Version
v1.0 - Initial Release (May 2026)

## License
© 2026 Data Scraping Pipeline
