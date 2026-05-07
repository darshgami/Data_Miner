#!/usr/bin/env python
"""
Quick usage examples for the Data Cleaning Pipeline
Run this file to see practical examples of how to use the API
"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from api.data_cleaner import DataCleaner
from api.test_data_generator import TestDataGenerator


def example_1_basic_cleaning():
    """Example 1: Clean a single record"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Record Cleaning")
    print("="*80)
    
    messy_record = {
        'Company Name': '  IBM CORPORATION  ',
        'Email': '  CONTACT@IBM.COM  ',
        'Phone No': '9876543210',
        'URL': 'www.ibm.com',
        'Address': 'New York, USA'
    }
    
    print("\nBefore:")
    for key, value in messy_record.items():
        print(f"  {key:15} : '{value}'")
    
    cleaner = DataCleaner()
    cleaned = cleaner.clean_record(messy_record)
    
    print("\nAfter:")
    for key, value in cleaned.items():
        print(f"  {key:15} : '{value}'")


def example_2_batch_cleaning():
    """Example 2: Clean multiple records with statistics"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Batch Cleaning with Statistics")
    print("="*80)
    
    # Generate test data
    generator = TestDataGenerator()
    records = generator.generate_dataset(count=20)
    
    print(f"\nGenerated {len(records)} messy records")
    
    # Clean them
    cleaner = DataCleaner()
    cleaned_records, skipped = cleaner.clean_dataset(records, remove_duplicates=True)
    
    # Show statistics
    stats = cleaner.get_summary_stats(cleaned_records)
    
    print(f"\nCleaning Results:")
    print(f"  Original Records   : {len(records)}")
    print(f"  After Cleanup      : {len(cleaned_records)}")
    print(f"  Skipped Records    : {len(skipped)}")
    print(f"\nData Quality:")
    print(f"  Complete Records   : {stats['Complete']} ({stats['Completion Rate']})")
    print(f"  Incomplete Records : {stats['Incomplete']}")
    print(f"  Suspicious Records : {stats['Suspicious']}")
    
    # Show first 3 cleaned records
    print(f"\nFirst 3 Cleaned Records:")
    for i, record in enumerate(cleaned_records[:3], 1):
        print(f"\n  Record {i}:")
        for key, value in record.items():
            print(f"    {key:15} : {value}")


def example_3_duplicate_detection():
    """Example 3: Detect and merge duplicates"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Duplicate Detection & Merging")
    print("="*80)
    
    duplicates = [
        {
            'Company Name': 'Microsoft Corporation',
            'Email': 'info@microsoft.com',
            'Phone No': '+1 4258828080',
            'URL': 'https://www.microsoft.com',
            'Address': 'Redmond, Washington'
        },
        {
            'Company Name': 'MICROSOFT CORPORATION',  # Duplicate with caps
            'Email': '',  # Missing email
            'Phone No': '',  # Missing phone
            'URL': 'https://microsoft.com',
            'Address': ''  # Missing address
        },
        {
            'Company Name': 'Microsoft Corporation ',  # Duplicate with space
            'Email': 'contact@microsoft.com',  # Different email
            'Phone No': '+1-425-882-8080',  # Same phone, different format
            'URL': '',  # Missing URL
            'Address': 'Redmond, WA 98052'  # Different address format
        }
    ]
    
    print("\nOriginal Records (3 duplicates with missing data):")
    for i, record in enumerate(duplicates, 1):
        print(f"\n  Record {i}:")
        for key, value in record.items():
            if value:
                print(f"    {key:15} : {value}")
            else:
                print(f"    {key:15} : (empty)")
    
    # Clean and merge
    cleaner = DataCleaner()
    cleaned, _ = cleaner.clean_dataset(duplicates, remove_duplicates=True)
    
    print(f"\n\nAfter Duplicate Merging (merged into 1 record):")
    for record in cleaned:
        print(f"\n  Merged Record:")
        for key, value in record.items():
            print(f"    {key:15} : {value}")


def example_4_validation_rules():
    """Example 4: Show validation rules in action"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Validation Rules")
    print("="*80)
    
    cleaner = DataCleaner()
    
    # Email validation
    print("\n1. EMAIL VALIDATION:")
    test_emails = [
        'valid.email@company.com',
        'test@test.com',                    # Fake domain
        '  info@company.com  ',             # Extra spaces
        'invalid@.com',                     # Invalid format
        'example@example.com',              # Fake domain
    ]
    
    print(f"\n{'Email':<30} {'Valid?':<10} {'Cleaned':<30}")
    print("-" * 70)
    for email in test_emails:
        is_valid = cleaner.is_valid_email(email)
        cleaned = cleaner.sanitize_email(email)
        status = "✓" if is_valid else "✗"
        print(f"{email:<30} {status:<10} {cleaned:<30}")
    
    # Phone validation
    print("\n2. PHONE STANDARDIZATION:")
    test_phones = [
        '9876543210',                       # 10 digits
        '+91 9876543210',                   # Already formatted
        '+91-98765-43210',                  # With dashes
        '(+91) 987-654-3210',               # With brackets
        '123',                              # Too short
        '9999999999999999',                 # Too long
    ]
    
    print(f"\n{'Phone':<30} {'Valid?':<10} {'Standardized':<30}")
    print("-" * 70)
    for phone in test_phones:
        is_valid = cleaner.is_valid_phone(phone)
        standardized = cleaner.standardize_phone(phone)
        status = "✓" if is_valid else "✗"
        print(f"{phone:<30} {status:<10} {standardized:<30}")
    
    # URL validation
    print("\n3. URL FIXING:")
    test_urls = [
        'https://www.company.com',          # Valid
        'www.company.com',                  # Missing protocol
        'company.com',                      # Missing protocol and www
        '  https://company.com  ',          # Extra spaces
        'htp://bad.com',                    # Typo in protocol
    ]
    
    print(f"\n{'URL':<35} {'Valid?':<10} {'Fixed':<35}")
    print("-" * 80)
    for url in test_urls:
        is_valid = cleaner.is_valid_url(url)
        fixed = cleaner.fix_url(url) if url.strip() else ""
        status = "✓" if is_valid else "✗"
        print(f"{url:<35} {status:<10} {fixed:<35}")


def example_5_quality_assessment():
    """Example 5: Data quality assessment"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Data Quality Assessment")
    print("="*80)
    
    test_records = [
        {
            'Company Name': 'Complete Company',
            'Email': 'info@company.com',
            'Phone No': '+919876543210',
            'URL': 'https://company.com',
            'Address': 'New York, USA'
        },
        {
            'Company Name': 'Incomplete Company',
            'Email': 'info@company.com',
            'Phone No': '+919876543210',
            'URL': '',  # Missing URL
            'Address': ''  # Missing address
        },
        {
            'Company Name': 'Suspicious Company',
            'Email': 'test@test.com',  # Fake email
            'Phone No': '123',  # Invalid phone
            'URL': 'no-protocol.com',  # Invalid URL
            'Address': ''
        }
    ]
    
    cleaner = DataCleaner()
    
    print(f"\n{'Company Name':<30} {'Status':<15} {'Issues':<50}")
    print("-" * 95)
    
    for record in test_records:
        status, issues = cleaner.assess_record_quality(record)
        issues_str = ", ".join(issues[:2]) if issues else "None"
        print(f"{record['Company Name']:<30} {status:<15} {issues_str:<50}")


def example_6_export_options():
    """Example 6: Export to Excel and CSV"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Export Options")
    print("="*80)
    
    # Generate and clean sample data
    generator = TestDataGenerator()
    records = generator.generate_dataset(count=10)
    
    cleaner = DataCleaner()
    cleaned_records, _ = cleaner.clean_dataset(records, remove_duplicates=True)
    
    # Create export directory
    export_dir = os.path.join(os.path.dirname(__file__), 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    # Export examples
    excel_file = os.path.join(export_dir, 'example_cleaned.xlsx')
    csv_file = os.path.join(export_dir, 'example_cleaned.csv')
    
    print(f"\nExporting {len(cleaned_records)} records...")
    
    # Export to Excel
    excel_ok = cleaner.export_to_excel(cleaned_records, excel_file)
    if excel_ok:
        size = os.path.getsize(excel_file) / 1024
        print(f"  ✓ Excel exported: {excel_file} ({size:.2f} KB)")
    else:
        print(f"  ✗ Excel export failed")
    
    # Export to CSV
    csv_ok = cleaner.export_to_csv(cleaned_records, csv_file)
    if csv_ok:
        size = os.path.getsize(csv_file) / 1024
        print(f"  ✓ CSV exported: {csv_file} ({size:.2f} KB)")
    else:
        print(f"  ✗ CSV export failed")


def example_7_complete_workflow():
    """Example 7: Complete workflow from messy to clean"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Complete Workflow")
    print("="*80)
    
    print("\nStep 1: Generate messy data...")
    generator = TestDataGenerator()
    messy_data = generator.generate_dataset(count=25)
    
    print(f"  Generated {len(messy_data)} messy records with:")
    print("    - Duplicate company names")
    print("    - Invalid emails")
    print("    - Malformed phone numbers")
    print("    - Incomplete URLs")
    print("    - Fragmented addresses")
    
    print("\nStep 2: Clean and validate...")
    cleaner = DataCleaner()
    cleaned_data, skipped = cleaner.clean_dataset(messy_data, remove_duplicates=True)
    
    print(f"  Result: {len(messy_data)} → {len(cleaned_data)} unique records")
    
    print("\nStep 3: Assess quality...")
    stats = cleaner.get_summary_stats(cleaned_data)
    
    print(f"  Total        : {stats['Total Records']}")
    print(f"  Complete     : {stats['Complete']} ({stats['Completion Rate']})")
    print(f"  Incomplete   : {stats['Incomplete']}")
    print(f"  Suspicious   : {stats['Suspicious']}")
    
    print("\nStep 4: Export...")
    export_dir = os.path.join(os.path.dirname(__file__), 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    excel_file = os.path.join(export_dir, 'complete_workflow_example.xlsx')
    success = cleaner.export_to_excel(cleaned_data, excel_file)
    
    if success:
        print(f"  ✓ Exported to: {excel_file}")
        print(f"\nWorkflow Complete!")
        print(f"  Input : {len(messy_data)} messy records")
        print(f"  Output: {len(cleaned_data)} clean records")
        print(f"  File  : {os.path.basename(excel_file)}")
    else:
        print(f"  ✗ Export failed")


def main():
    """Run all examples"""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + "DATA CLEANING PIPELINE - USAGE EXAMPLES".center(78) + "║")
    print("╚" + "="*78 + "╝")
    
    examples = [
        ("1. Basic Record Cleaning", example_1_basic_cleaning),
        ("2. Batch Cleaning with Statistics", example_2_batch_cleaning),
        ("3. Duplicate Detection & Merging", example_3_duplicate_detection),
        ("4. Validation Rules", example_4_validation_rules),
        ("5. Data Quality Assessment", example_5_quality_assessment),
        ("6. Export Options", example_6_export_options),
        ("7. Complete Workflow", example_7_complete_workflow),
    ]
    
    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n✗ Error in {name}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80 + "\n")
    
    print("Check the 'exports/' folder for generated Excel and CSV files.")
    print("\nFor API usage, see README.md")


if __name__ == '__main__':
    main()
