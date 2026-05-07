"""
Comprehensive data cleaning, validation, and standardization module.
Handles: deduplication, validation, standardization, and quality flagging.
"""

import re
from typing import List, Dict, Tuple, Optional
from urllib.parse import urlparse
import pandas as pd


class DataCleaner:
    """Main data cleaning and validation class"""
    
    # Invalid/test email domains
    FAKE_EMAIL_DOMAINS = {
        'example.com', 'test.com', 'domain.com', 'mail.com', 'company.com',
        'business.com', 'website.com', 'gmail.test', 'email.test', 'fake.com',
        'sample.com', 'demo.com', 'placeholder.com', 'noemail.com'
    }
    
    # Regex patterns
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_REGEX = r'^\+?(?:1-)?(?:\d{1,4}[-.\s]?)?(?:\(?\d{1,4}\)?[-.\s]?)?(\d{3,4}[-.\s]?\d{3,4}|\d{5,14})$'
    URL_REGEX = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/.*)?$'
    
    def __init__(self):
        self.cleaned_records = []
        self.duplicate_groups = []
        
    # ============ EMAIL VALIDATION ============
    
    def is_valid_email(self, email: str) -> bool:
        """Check if email is valid and not fake"""
        if not email or email.lower() in ['n/a', 'na', 'none', '']:
            return False
        
        email = email.strip().lower()
        
        # Check format
        if not re.match(self.EMAIL_REGEX, email):
            return False
        
        # Extract domain
        domain = email.split('@')[1]
        
        # Check against fake domains
        if domain in self.FAKE_EMAIL_DOMAINS:
            return False
        
        # Check for obvious test patterns
        if any(pattern in email for pattern in ['test@', 'example@', 'admin@', 'noreply@']):
            return False
        
        return True
    
    def sanitize_email(self, email: str) -> str:
        """Clean and standardize email"""
        if not email:
            return ""
        
        email = email.strip().lower()
        
        # Remove common prefixes/suffixes
        email = re.sub(r'^mailto:', '', email)
        email = re.sub(r'[<>"\']', '', email)
        
        return email if self.is_valid_email(email) else ""
    
    # ============ PHONE VALIDATION ============
    
    def is_valid_phone(self, phone: str) -> bool:
        """Check if phone number is valid"""
        if not phone or phone.lower() in ['n/a', 'na', 'none', '']:
            return False
        
        phone = phone.strip()
        
        # Remove common separators
        digits_only = re.sub(r'[^\d+]', '', phone)
        
        # Check length (8-15 digits typical for international)
        if len(digits_only) < 8 or len(digits_only) > 15:
            return False
        
        # Check for too many repeated digits
        if len(set(digits_only.replace('+', ''))) == 1:
            return False
        
        return True
    
    def standardize_phone(self, phone: str, country_code: str = '+91') -> str:
        """Standardize phone to international format"""
        if not phone or not self.is_valid_phone(phone):
            return ""
        
        phone = phone.strip()
        
        # Remove all non-digit/+ chars
        digits_only = re.sub(r'[^\d+]', '', phone)
        
        # Remove + if present to process
        digits_clean = digits_only.replace('+', '')
        
        # If already has country code (starts with known codes)
        if digits_only.startswith('+'):
            return f"+{digits_only.lstrip('+')}"
        
        # Add country code if missing
        if not digits_clean.startswith('91') and not digits_clean.startswith('1'):
            if len(digits_clean) == 10:  # Indian format
                return f"{country_code}{digits_clean}"
        
        return f"+{digits_clean}"
    
    # ============ URL VALIDATION & CLEANING ============
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and complete"""
        if not url or url.lower() in ['n/a', 'na', 'none', '']:
            return False
        
        url = url.strip()
        
        # Must have protocol
        if not url.startswith(('http://', 'https://')):
            return False
        
        try:
            result = urlparse(url)
            # Check basic URL structure
            if result.netloc and result.scheme in ['http', 'https']:
                return True
        except:
            pass
        
        return False
    
    def fix_url(self, url: str) -> str:
        """Fix incomplete URLs"""
        if not url:
            return ""
        
        url = url.strip()
        
        # Already valid
        if self.is_valid_url(url):
            return url
        
        # Remove common junk
        url = re.sub(r'[<>"\'\s]', '', url)
        
        # Add protocol if missing
        if url and not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        # Validate again
        return url if self.is_valid_url(url) else ""
    
    # ============ COMPANY NAME STANDARDIZATION ============
    
    def standardize_company_name(self, name: str) -> str:
        """Normalize company name"""
        if not name:
            return ""
        
        name = name.strip()
        
        # Fix capitalization
        name = ' '.join(word.capitalize() for word in name.split())
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name)
        
        # Remove common redundant suffixes if they appear multiple times
        common_suffixes = [' pvt', ' ltd', ' llc', ' inc', ' corp', ' co', ' kft', ' gmbh']
        
        # Only remove if seems redundant
        for suffix in common_suffixes:
            if name.lower().count(suffix) > 1:
                name = name.lower().replace(suffix, '', 1).strip()
        
        return name
    
    def get_company_key(self, name: str) -> str:
        """Get normalized key for deduplication matching"""
        if not name:
            return ""
        
        # Lowercase, remove punctuation, normalize spaces
        key = name.lower()
        key = re.sub(r'[^\w\s]', '', key)
        key = re.sub(r'\s+', ' ', key).strip()
        
        # Remove common suffixes for matching
        suffixes = ['pvt ltd', 'private limited', 'ltd', 'llc', 'inc', 'corp', 'corporation', 'company', 'co']
        for suffix in suffixes:
            key = re.sub(rf'\s*{suffix}\s*$', '', key)
        
        return key.strip()
    
    # ============ ADDRESS CLEANING ============
    
    def clean_address(self, address: str) -> str:
        """Clean and standardize address"""
        if not address:
            return ""
        
        address = address.strip()
        
        # Remove extra whitespace and newlines
        address = re.sub(r'\s+', ' ', address)
        
        # Remove common junk characters
        address = re.sub(r'[\[\]\<\>\"\'`|]', '', address)
        
        # Remove leading/trailing punctuation
        address = re.sub(r'^[^a-zA-Z0-9]+', '', address)
        address = re.sub(r'[^a-zA-Z0-9]+$', '', address)
        
        return address.strip()
    
    # ============ DUPLICATE DETECTION & MERGING ============
    
    def find_duplicate_groups(self, records: List[Dict]) -> List[List[int]]:
        """Find groups of duplicate records by company name"""
        groups = {}
        
        for idx, record in enumerate(records):
            company_key = self.get_company_key(record.get('Company Name', ''))
            if company_key:
                if company_key not in groups:
                    groups[company_key] = []
                groups[company_key].append(idx)
        
        # Return only groups with 2+ items
        return [indices for indices in groups.values() if len(indices) > 1]
    
    def merge_records(self, records: List[Dict], group_indices: List[int]) -> Dict:
        """Merge multiple duplicate records, preferring most complete data"""
        if not group_indices:
            return {}
        
        if len(group_indices) == 1:
            return records[group_indices[0]]
        
        # Sort by completeness (non-empty fields count)
        sorted_indices = sorted(
            group_indices,
            key=lambda i: sum(1 for v in records[i].values() if v and str(v).strip() and v != ''),
            reverse=True
        )
        
        # Start with most complete record
        merged = dict(records[sorted_indices[0]])
        
        # Fill in missing fields from other records
        fields_to_merge = ['Email', 'Phone No', 'URL', 'Address']
        for field in fields_to_merge:
            if not merged.get(field) or merged.get(field) == '':
                for idx in sorted_indices[1:]:
                    candidate = records[idx].get(field, '')
                    if candidate and str(candidate).strip() and candidate != '':
                        merged[field] = candidate
                        break
        
        return merged
    
    # ============ RECORD QUALITY ASSESSMENT ============
    
    def assess_record_quality(self, record: Dict) -> Tuple[str, List[str]]:
        """
        Assess record completeness and validity.
        Returns: (status, issues_list)
        """
        company = record.get('Company Name', '').strip()
        email = record.get('Email', '').strip()
        phone = record.get('Phone No', '').strip()
        url = record.get('URL', '').strip()
        address = record.get('Address', '').strip()
        
        issues = []
        key_fields_present = 0
        
        # Company name check
        if not company:
            issues.append("missing_company_name")
        else:
            key_fields_present += 1
        
        # Email check
        if email and self.is_valid_email(email):
            key_fields_present += 1
        elif email:
            issues.append("invalid_email")
        else:
            issues.append("missing_email")
        
        # Phone check
        if phone and self.is_valid_phone(phone):
            key_fields_present += 1
        elif phone:
            issues.append("invalid_phone")
        else:
            issues.append("missing_phone")
        
        # URL check
        if url and self.is_valid_url(url):
            key_fields_present += 1
        elif url:
            issues.append("invalid_url")
        else:
            issues.append("missing_url")
        
        # Address check
        if not address:
            issues.append("missing_address")
        
        # Determine status
        if key_fields_present >= 4:
            status = "Complete"
        elif key_fields_present >= 3:
            status = "Incomplete"
        else:
            status = "Suspicious"
        
        # Add suspicious markers
        if any(x in issues for x in ['invalid_email', 'invalid_phone', 'invalid_url']):
            status = "Suspicious"
        
        return status, issues
    
    # ============ MAIN CLEANING PIPELINE ============
    
    def clean_record(self, record: Dict) -> Dict:
        """Clean individual record"""
        cleaned = {}
        
        # Company name
        company = record.get('Company Name', '').strip()
        cleaned['Company Name'] = self.standardize_company_name(company)
        
        # Email
        email = record.get('Email', '').strip()
        cleaned['Email'] = self.sanitize_email(email)
        
        # Phone
        phone = record.get('Phone No', '').strip()
        if phone:
            phone = self.standardize_phone(phone)
        cleaned['Phone No'] = phone
        
        # URL
        url = record.get('URL', '').strip()
        cleaned['URL'] = self.fix_url(url)
        
        # Address
        address = record.get('Address', '').strip()
        cleaned['Address'] = self.clean_address(address)
        
        return cleaned
    
    def clean_dataset(self, records: List[Dict], remove_duplicates: bool = True) -> Tuple[List[Dict], List[Dict]]:
        """
        Main cleaning pipeline.
        Returns: (cleaned_records, skipped_records)
        """
        cleaned_data = []
        skipped_data = []
        seen_companies = set()
        
        # Step 1: Find duplicate groups
        if remove_duplicates:
            dup_groups = self.find_duplicate_groups(records)
            processed_indices = set()
            
            for group in dup_groups:
                merged = self.merge_records(records, group)
                if merged:
                    cleaned = self.clean_record(merged)
                    company_key = self.get_company_key(cleaned.get('Company Name', ''))
                    
                    if company_key and company_key not in seen_companies:
                        status, issues = self.assess_record_quality(cleaned)
                        cleaned['Status'] = status
                        cleaned_data.append(cleaned)
                        seen_companies.add(company_key)
                
                processed_indices.update(group)
            
            # Process non-duplicate records
            for idx, record in enumerate(records):
                if idx not in processed_indices:
                    cleaned = self.clean_record(record)
                    company_key = self.get_company_key(cleaned.get('Company Name', ''))
                    
                    if company_key and company_key not in seen_companies:
                        status, issues = self.assess_record_quality(cleaned)
                        cleaned['Status'] = status
                        cleaned_data.append(cleaned)
                        seen_companies.add(company_key)
        else:
            # Just clean without deduplication
            for record in records:
                cleaned = self.clean_record(record)
                company_key = self.get_company_key(cleaned.get('Company Name', ''))
                
                if company_key and company_key not in seen_companies:
                    status, issues = self.assess_record_quality(cleaned)
                    cleaned['Status'] = status
                    cleaned_data.append(cleaned)
                    seen_companies.add(company_key)
        
        return cleaned_data, skipped_data
    
    # ============ EXPORT UTILITIES ============
    
    def to_dataframe(self, records: List[Dict]) -> pd.DataFrame:
        """Convert cleaned records to pandas DataFrame"""
        df = pd.DataFrame(records)
        
        # Ensure correct column order
        columns = ['Company Name', 'Email', 'Phone No', 'URL', 'Address', 'Status']
        available_cols = [c for c in columns if c in df.columns]
        df = df[available_cols]
        
        return df
    
    def export_to_excel(self, records: List[Dict], filepath: str) -> bool:
        """Export records to Excel file"""
        try:
            df = self.to_dataframe(records)
            
            # Use openpyxl for better formatting
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Cleaned Data', index=False)
                
                # Get worksheet to add formatting
                worksheet = writer.sheets['Cleaned Data']
                
                # Set column widths
                worksheet.column_dimensions['A'].width = 25
                worksheet.column_dimensions['B'].width = 30
                worksheet.column_dimensions['C'].width = 20
                worksheet.column_dimensions['D'].width = 35
                worksheet.column_dimensions['E'].width = 40
                worksheet.column_dimensions['F'].width = 12
                
                # Freeze header row
                worksheet.freeze_panes = 'A2'
            
            return True
        except Exception as e:
            print(f"Error exporting to Excel: {str(e)}")
            return False
    
    def export_to_csv(self, records: List[Dict], filepath: str) -> bool:
        """Export records to CSV file"""
        try:
            df = self.to_dataframe(records)
            df.to_csv(filepath, index=False, encoding='utf-8')
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {str(e)}")
            return False
    
    def get_summary_stats(self, records: List[Dict]) -> Dict:
        """Get statistics about cleaned dataset"""
        total = len(records)
        complete = len([r for r in records if r.get('Status') == 'Complete'])
        incomplete = len([r for r in records if r.get('Status') == 'Incomplete'])
        suspicious = len([r for r in records if r.get('Status') == 'Suspicious'])
        
        return {
            'Total Records': total,
            'Complete': complete,
            'Incomplete': incomplete,
            'Suspicious': suspicious,
            'Completion Rate': f"{(complete/total*100):.1f}%" if total > 0 else "0%"
        }
