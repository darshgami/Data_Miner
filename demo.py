#!/usr/bin/env python
"""
Complete demonstration of the data cleaning pipeline
Shows: Generate messy data -> Clean -> Export to Excel
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from api.data_cleaner import DataCleaner
from api.test_data_generator import TestDataGenerator
import json
from datetime import datetime


def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_table(data, headers):
    """Print formatted table"""
    # Calculate column widths
    col_widths = []
    for i, header in enumerate(headers):
        max_width = len(str(header))
        for row in data:
            max_width = max(max_width, len(str(row[i])))
        col_widths.append(max_width + 2)
    
    # Print header
    header_row = " | ".join(f"{h:^{col_widths[i]-2}}" for i, h in enumerate(headers))
    print(header_row)
    print("-" * len(header_row))
    
    # Print rows
    for row in data:
        print(" | ".join(f"{str(v):^{col_widths[i]-2}}" for i, v in enumerate(row)))


def demo_data_generation():
    """Demo 1: Generate realistic messy test data"""
    print_section("1. GENERATING REALISTIC MESSY TEST DATA")
    
    print("Creating test data with various issues:")
    print("  ✓ Duplicate company names (with variations)")
    print("  ✓ Invalid/fake emails")
    print("  ✓ Incomplete/incorrectly formatted phone numbers")
    print("  ✓ Missing or partial URLs")
    print("  ✓ Fragmented or shifted addresses")
    print("  ✓ Misaligned data in wrong columns")
    print()
    
    generator = TestDataGenerator()
    records = generator.generate_dataset(count=30, include_fakes=True, 
                                        include_duplicates=True, include_shifted=True)
    
    print(f"Generated {len(records)} records\n")
    
    # Show sample of messy data
    print("Sample of MESSY DATA (before cleaning):")
    print("-" * 150)
    for i, record in enumerate(records[:3]):
        print(f"\nRecord {i+1}:")
        for key, value in record.items():
            print(f"  {key:15} : {str(value)[:80]}")
    
    return records


def demo_data_cleaning(messy_records):
    """Demo 2: Clean and validate the messy data"""
    print_section("2. CLEANING & VALIDATING DATA")
    
    print("Running data cleaning pipeline...")
    print("  ✓ Removing duplicate company names")
    print("  ✓ Validating and standardizing emails")
    print("  ✓ Converting phone numbers to international format")
    print("  ✓ Fixing and validating URLs")
    print("  ✓ Cleaning addresses")
    print("  ✓ Assessing data quality")
    print()
    
    cleaner = DataCleaner()
    cleaned_records, skipped = cleaner.clean_dataset(messy_records, remove_duplicates=True)
    
    print(f"Original records: {len(messy_records)}")
    print(f"After deduplication: {len(cleaned_records)}")
    print(f"Skipped records: {len(skipped)}")
    print()
    
    # Show sample of cleaned data
    print("Sample of CLEANED DATA (after cleaning):")
    print("-" * 150)
    for i, record in enumerate(cleaned_records[:3]):
        print(f"\nRecord {i+1}:")
        for key, value in record.items():
            print(f"  {key:15} : {str(value)[:80]}")
    
    return cleaned_records, cleaner


def demo_data_statistics(cleaned_records, cleaner):
    """Demo 3: Show data quality statistics"""
    print_section("3. DATA QUALITY STATISTICS")
    
    stats = cleaner.get_summary_stats(cleaned_records)
    
    print(f"Total Records       : {stats['Total Records']}")
    print(f"Complete Records    : {stats['Complete']} ✓")
    print(f"Incomplete Records  : {stats['Incomplete']} ⚠")
    print(f"Suspicious Records  : {stats['Suspicious']} ✗")
    print(f"Completion Rate     : {stats['Completion Rate']}")
    print()
    
    # Show breakdown by status
    status_breakdown = {}
    for record in cleaned_records:
        status = record.get('Status', 'Unknown')
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
    
    print("Records by Status:")
    for status, count in status_breakdown.items():
        percentage = (count / len(cleaned_records) * 100) if cleaned_records else 0
        print(f"  {status:12} : {count:3} ({percentage:5.1f}%)")


def demo_data_export(cleaned_records, cleaner):
    """Demo 4: Export cleaned data to Excel"""
    print_section("4. EXPORTING TO EXCEL")
    
    # Create exports directory
    exports_dir = os.path.join(os.path.dirname(__file__), 'exports')
    os.makedirs(exports_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_file = os.path.join(exports_dir, f'cleaned_data_{timestamp}.xlsx')
    csv_file = os.path.join(exports_dir, f'cleaned_data_{timestamp}.csv')
    
    print(f"Exporting to Excel: {excel_file}")
    excel_success = cleaner.export_to_excel(cleaned_records, excel_file)
    
    if excel_success:
        file_size = os.path.getsize(excel_file) / 1024  # KB
        print(f"  ✓ SUCCESS - File size: {file_size:.2f} KB")
    else:
        print(f"  ✗ FAILED")
    
    print(f"\nExporting to CSV: {csv_file}")
    csv_success = cleaner.export_to_csv(cleaned_records, csv_file)
    
    if csv_success:
        file_size = os.path.getsize(csv_file) / 1024  # KB
        print(f"  ✓ SUCCESS - File size: {file_size:.2f} KB")
    else:
        print(f"  ✗ FAILED")
    
    print(f"\n✓ Files exported to: {exports_dir}")


def demo_data_comparison():
    """Demo 5: Show before/after comparison"""
    print_section("5. BEFORE & AFTER COMPARISON")
    
    generator = TestDataGenerator()
    
    print("\n" + "="*100)
    print("EXAMPLE 1: Email Validation")
    print("="*100)
    
    emails = [
        "test@test.com",           # Fake domain
        "  contact@company.com  ", # Extra spaces
        "invalid@.com",            # Invalid format
        "info@realcompany.com",    # Valid
    ]
    
    cleaner = DataCleaner()
    
    print(f"\n{'ORIGINAL':<35} | {'CLEANED':<35} | {'VALID':<10}")
    print("-" * 82)
    for email in emails:
        cleaned = cleaner.sanitize_email(email)
        valid = "✓" if cleaner.is_valid_email(cleaned) else "✗"
        print(f"{email:<35} | {cleaned:<35} | {valid:<10}")
    
    print("\n" + "="*100)
    print("EXAMPLE 2: Phone Number Standardization")
    print("="*100)
    
    phones = [
        "9876543210",              # 10 digits
        "+91 (987) 654-3210",      # Formatted
        "011-2345 6789",           # Landline
        "123",                     # Too short
    ]
    
    print(f"\n{'ORIGINAL':<35} | {'STANDARDIZED':<35} | {'VALID':<10}")
    print("-" * 82)
    for phone in phones:
        standardized = cleaner.standardize_phone(phone)
        valid = "✓" if cleaner.is_valid_phone(standardized) else "✗"
        print(f"{phone:<35} | {standardized:<35} | {valid:<10}")
    
    print("\n" + "="*100)
    print("EXAMPLE 3: URL Fixing")
    print("="*100)
    
    urls = [
        "www.company.com",         # Missing protocol
        "  https://company.com  ", # Extra spaces
        "htp://bad.com",           # Typo
        "https://example.com",     # Valid
    ]
    
    print(f"\n{'ORIGINAL':<35} | {'FIXED':<35} | {'VALID':<10}")
    print("-" * 82)
    for url in urls:
        fixed = cleaner.fix_url(url)
        valid = "✓" if cleaner.is_valid_url(fixed) else "✗"
        print(f"{url:<35} | {fixed:<35} | {valid:<10}")


def demo_full_pipeline_summary():
    """Demo 6: Complete pipeline summary"""
    print_section("6. COMPLETE PIPELINE SUMMARY")
    
    print("""
┌─────────────────────────────────────────────────────────────────────────┐
│  DATA CLEANING PIPELINE CAPABILITIES                                   │
└─────────────────────────────────────────────────────────────────────────┘

1. DEDUPLICATION
   ✓ Case-insensitive company name matching
   ✓ Identifies duplicate entries with slight variations
   ✓ Merges records keeping most complete information

2. EMAIL VALIDATION
   ✓ Validates email format (RFC compliance)
   ✓ Rejects fake domains (test@test.com, example@example.com, etc.)
   ✓ Detects and removes test patterns
   ✓ Standardizes to lowercase

3. PHONE STANDARDIZATION
   ✓ Converts to international format (+91XXXXXXXXXX)
   ✓ Validates length (8-15 digits)
   ✓ Removes invalid patterns
   ✓ Handles multiple formats (with/without country code, with dashes, etc.)

4. URL CLEANING
   ✓ Ensures protocol (http:// or https://)
   ✓ Validates URL structure
   ✓ Removes extra whitespace
   ✓ Fixes common typos

5. ADDRESS CLEANING
   ✓ Removes special characters and junk
   ✓ Consolidates fragmented addresses
   ✓ Standardizes spacing

6. DATA QUALITY ASSESSMENT
   ✓ "Complete"   - All key fields present and valid
   ✓ "Incomplete" - Missing some fields
   ✓ "Suspicious" - Invalid data or too many missing fields

7. EXCEL/CSV EXPORT
   ✓ Formatted Excel with headers and proper column widths
   ✓ CSV for easy import to other tools
   ✓ Summary statistics included

┌─────────────────────────────────────────────────────────────────────────┐
│  SAMPLE WORKFLOW                                                        │
└─────────────────────────────────────────────────────────────────────────┘

INPUT (Messy Data):
  • Company Name: "Tata Steel  Ltd "
  • Email: "  info@EXAMPLE.COM  "
  • Phone: "9876543210"
  • URL: "www.company.com"
  • Address: "Plot 123 | Mumbai"

OUTPUT (Cleaned Data):
  • Company Name: "Tata Steel Ltd"
  • Email: "" (invalid - fake domain removed)
  • Phone: "+919876543210"
  • URL: "https://www.company.com"
  • Address: "Plot 123 Mumbai"
  • Status: "Incomplete" (missing email)

┌─────────────────────────────────────────────────────────────────────────┐
│  API ENDPOINTS (DJANGO REST)                                            │
└─────────────────────────────────────────────────────────────────────────┘

POST /api/test-data/
    Generate realistic messy test data
    Returns: List of records with various data quality issues

POST /api/clean/
    Clean and validate records
    Params: records (list), remove_duplicates (bool)
    Returns: Cleaned records + statistics

POST /api/export/
    Export records to Excel
    Params: records (list), filename (str)
    Returns: File path and confirmation

POST /api/pipeline/
    Complete pipeline (scrape/test → clean → export)
    Params: source ('test'/'scrape'), city, export_format ('excel'/'csv')
    Returns: Full summary with file path

POST /api/search/
    Scrape business data from web sources
    Params: city, pincode
    Returns: Raw scraped data

""")


def main():
    """Run complete demonstration"""
    print("\n")
    print("╔" + "═"*148 + "╗")
    print("║" + " "*148 + "║")
    print("║" + "DATA CLEANING PIPELINE - COMPREHENSIVE DEMONSTRATION".center(148) + "║")
    print("║" + " "*148 + "║")
    print("╚" + "═"*148 + "╝")
    
    try:
        # Run demos
        messy_records = demo_data_generation()
        cleaned_records, cleaner = demo_data_cleaning(messy_records)
        demo_data_statistics(cleaned_records, cleaner)
        demo_data_export(cleaned_records, cleaner)
        demo_data_comparison()
        demo_full_pipeline_summary()
        
        print_section("DEMONSTRATION COMPLETE ✓")
        print("""
The data cleaning pipeline is ready to use!

Next Steps:
1. Start the Django server: python manage.py runserver
2. Use the API endpoints to:
   - Generate test data: POST /api/test-data/
   - Clean your data: POST /api/clean/
   - Export to Excel: POST /api/export/
   - Run full pipeline: POST /api/pipeline/
3. Check the 'exports' folder for generated Excel files

For more information, see the README.md file.
        """)
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
