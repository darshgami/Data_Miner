"""
Test data generator - Creates realistic messy company data with various issues
to simulate real-world scenarios for testing the data cleaner.
"""

import random
from typing import List, Dict
from faker import Faker

fake = Faker('en_IN')  # India locale for realistic Indian company data


class TestDataGenerator:
    """Generate realistic messy test data"""
    
    COMPANY_SUFFIXES = ['Pvt Ltd', 'Ltd', 'LLC', 'Inc', 'Corporation', 'Co', 'KFT', 'GmbH', 
                        'PRIVATE LIMITED', 'Enterprises', 'Industries', 'Traders', 'Solutions']
    
    COMPANY_PREFIXES = ['Global', 'Prime', 'National', 'Indian', 'Digital', 'Smart', 'Advanced',
                        'Tech', 'Innovative', 'Leading', 'Professional', 'Enterprise']
    
    INDUSTRIES = ['Manufacturing', 'Electronics', 'Textiles', 'Chemicals', 'Engineering',
                  'Construction', 'IT Services', 'Logistics', 'Trading', 'Export',
                  'Import', 'Consulting', 'Healthcare', 'Education', 'Retail']
    
    CITIES = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 
              'Pune', 'Ahmedabad', 'Gurgaon', 'Noida', 'Thane', 'Nashik', 'Indore']
    
    def __init__(self):
        self.fake = Faker('en_IN')
        random.seed(42)
    
    def generate_company_name(self) -> str:
        """Generate realistic company name"""
        choice = random.choice([1, 2, 3])
        
        if choice == 1:
            # Real-looking name with prefix and suffix
            name = f"{random.choice(self.COMPANY_PREFIXES)} {random.choice(self.INDUSTRIES)} {random.choice(self.COMPANY_SUFFIXES)}"
        elif choice == 2:
            # Name with city
            city = random.choice(self.CITIES)
            name = f"{city} {random.choice(self.INDUSTRIES)} {random.choice(self.COMPANY_SUFFIXES)}"
        else:
            # Simple name
            name = f"{self.fake.word().title()} {self.fake.word().title()} {random.choice(self.COMPANY_SUFFIXES)}"
        
        return name
    
    def generate_email(self, company_name: str = None, include_fake: bool = False) -> str:
        """Generate email with various issues"""
        issues = random.choice([1, 2, 3, 4, 5, 6])
        
        if include_fake and issues == 6:
            # Fake email
            return random.choice(['test@test.com', 'example@example.com', 'contact@domain.com', 
                                 'info@mail.com', 'admin@admin.com', 'noemail@fake.com'])
        
        if issues == 1:
            # Normal email
            if company_name:
                domain = company_name.split()[0].lower()
            else:
                domain = self.fake.domain_name()
            return f"info@{domain}.com"
        elif issues == 2:
            # With extra spaces
            domain = self.fake.domain_name()
            return f"  contact@{domain}.com  "
        elif issues == 3:
            # Multiple emails (just return first)
            return f"info@{self.fake.domain_name()}.com, contact@{self.fake.domain_name()}.com"
        elif issues == 4:
            # Malformed
            return f"info@.{self.fake.domain_name()}"
        else:
            # Missing email
            return ""
    
    def generate_phone(self) -> str:
        """Generate phone number with various issues"""
        issues = random.choice([1, 2, 3, 4, 5, 6, 7])
        
        if issues == 1:
            # Proper Indian format
            return f"+91 {random.randint(9000000000, 9999999999)}"
        elif issues == 2:
            # Without country code
            return str(random.randint(9000000000, 9999999999))
        elif issues == 3:
            # With extra spaces/dashes
            phone = f"+91-{random.randint(9000000000, 9999999999)}"
            return phone
        elif issues == 4:
            # Partial/incomplete
            return str(random.randint(900000, 999999))
        elif issues == 5:
            # With brackets and spaces
            num = random.randint(9000000000, 9999999999)
            return f"(+91) {str(num)[:5]}-{str(num)[5:]}"
        elif issues == 6:
            # Landline format
            return f"011-{random.randint(40000000, 49999999)}"
        else:
            # Missing phone
            return ""
    
    def generate_url(self, company_name: str = None) -> str:
        """Generate URL with various issues"""
        issues = random.choice([1, 2, 3, 4, 5, 6, 7])
        
        if issues == 1:
            # Proper URL
            if company_name:
                domain = company_name.split()[0].lower()
            else:
                domain = self.fake.domain_name().split('.')[0]
            return f"https://www.{domain}.com"
        elif issues == 2:
            # Without protocol
            return f"www.{self.fake.domain_name()}"
        elif issues == 3:
            # Partial URL
            return f"company{random.randint(1, 9999)}"
        elif issues == 4:
            # With extra spaces
            return f"  https://www.{self.fake.domain_name()}  "
        elif issues == 5:
            # Wrong format
            return f"htp://www.{self.fake.domain_name()}"
        elif issues == 6:
            # Multiple URLs
            url1 = f"https://www.{self.fake.domain_name()}"
            url2 = f"https://www.{self.fake.domain_name()}"
            return f"{url1} | {url2}"
        else:
            # Missing URL
            return ""
    
    def generate_address(self, city: str = None) -> str:
        """Generate address with various issues"""
        issues = random.choice([1, 2, 3, 4, 5, 6, 7])
        
        if issues == 1:
            # Complete address
            if not city:
                city = random.choice(self.CITIES)
            return f"Plot {random.randint(1, 500)}, GIDC Area, {city}, {random.randint(400000, 500000)}"
        elif issues == 2:
            # Partial address
            return f"Plot {random.randint(1, 500)}, {random.choice(self.CITIES)}"
        elif issues == 3:
            # With extra symbols
            return f"###Plot {random.randint(1, 500)}, @@@ {random.choice(self.CITIES)} <>"
        elif issues == 4:
            # Multiple lines concatenated poorly
            return f"Plot 123\nBuilding B\nCity {random.choice(self.CITIES)}\n"
        elif issues == 5:
            # Fragmented
            parts = [f"Plot {random.randint(1,500)}", "Near Railway Station", random.choice(self.CITIES)]
            return " | ".join(parts) if random.choice([True, False]) else " | ".join(parts) + " | "
        elif issues == 6:
            # Shifted/misaligned (wrong data)
            return fake.phone_number()
        else:
            # Missing
            return ""
    
    def generate_dataset(self, count: int = 50, include_fakes: bool = True, 
                        include_duplicates: bool = True, include_shifted: bool = True) -> List[Dict]:
        """Generate complete messy dataset"""
        records = []
        generated_companies = {}
        
        for i in range(count):
            # Generate base company
            company_name = self.generate_company_name()
            
            # Optionally create duplicates
            if include_duplicates and random.random() < 0.15:  # 15% chance of duplicate
                if generated_companies:
                    # Use existing company with variations
                    orig_company = random.choice(list(generated_companies.keys()))
                    # Slight variation (e.g., capitalization, spacing)
                    if random.choice([True, False]):
                        company_name = orig_company.upper()
                    else:
                        company_name = orig_company + " "
            else:
                generated_companies[company_name] = True
            
            city = random.choice(self.CITIES)
            
            # Create record
            record = {
                'Company Name': company_name,
                'Email': self.generate_email(company_name, include_fakes),
                'Phone No': self.generate_phone(),
                'URL': self.generate_url(company_name),
                'Address': self.generate_address(city)
            }
            
            # Randomly shift data to wrong columns (10% chance)
            if include_shifted and random.random() < 0.10:
                values = list(record.values())[1:]  # Skip company name
                random.shuffle(values)
                keys = list(record.keys())[1:]
                for key, value in zip(keys, values):
                    record[key] = value
            
            records.append(record)
        
        return records
    
    def generate_real_data_samples(self) -> List[Dict]:
        """Generate realistic sample data for specific companies"""
        real_companies = [
            {
                'Company Name': 'Tata Steel Limited',
                'Email': 'contact@tatasteel.com',
                'Phone No': '+91 651 2290 000',
                'URL': 'https://www.tatasteel.com',
                'Address': 'Jamshedpur, Jharkhand 831001'
            },
            {
                'Company Name': 'Reliance Industries Ltd',
                'Email': 'info@ril.com',
                'Phone No': '+91 22 3555 5000',
                'URL': 'https://www.reliance.com',
                'Address': 'Navi Mumbai, Maharashtra 400710'
            },
            {
                'Company Name': 'HDFC Bank',
                'Email': 'support@hdfcbank.com',
                'Phone No': '+91 1860 500 5555',
                'URL': 'https://www.hdfcbank.com',
                'Address': 'Mumbai, Maharashtra 400001'
            },
            {
                'Company Name': 'Infosys Limited',
                'Email': 'contact@infosys.com',
                'Phone No': '+91 80 4156 0000',
                'URL': 'https://www.infosys.com',
                'Address': 'Bangalore, Karnataka 560034'
            },
            {
                'Company Name': 'ITC Limited',
                'Email': 'info@itcportal.com',
                'Phone No': '+91 33 2208 1000',
                'URL': 'https://www.itcportal.com',
                'Address': 'Kolkata, West Bengal 700001'
            }
        ]
        
        return real_companies


def create_sample_excel_dataset(filepath: str = 'd:\\Data_Scraping\\sample_messy_data.csv'):
    """Create and save sample messy dataset"""
    generator = TestDataGenerator()
    records = generator.generate_dataset(count=100, include_fakes=True, 
                                        include_duplicates=True, include_shifted=True)
    
    # Also add some real company samples
    real_samples = generator.generate_real_data_samples()
    # Mess up some real data
    for record in real_samples:
        if random.choice([True, False]):
            record['Email'] = record['Email'].upper() + " "
        if random.choice([True, False]):
            record['Phone No'] = " " + record['Phone No']
    
    all_records = records + real_samples
    
    # Convert to DataFrame and export
    import pandas as pd
    df = pd.DataFrame(all_records)
    df.to_csv(filepath, index=False, encoding='utf-8')
    
    print(f"Sample dataset created: {filepath}")
    print(f"Total records: {len(all_records)}")
    return filepath


if __name__ == '__main__':
    # Generate sample data
    create_sample_excel_dataset()
