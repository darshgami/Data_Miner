from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
import os
from .scraper import scrape_data
from .data_cleaner import DataCleaner
from .test_data_generator import TestDataGenerator


@api_view(['POST'])
def search_data(request):
    """Scrape company data from web sources"""
    city = request.data.get("city", "")
    pincode = request.data.get("pincode", "")
    
    query = f"{city} {pincode}".strip()
    data = scrape_data(query)

    return Response(data)


@api_view(['POST'])
def generate_test_data(request):
    """Generate realistic messy test data"""
    count = request.data.get('count', 50)
    include_fakes = request.data.get('include_fakes', True)
    include_duplicates = request.data.get('include_duplicates', True)
    include_shifted = request.data.get('include_shifted', True)
    
    try:
        generator = TestDataGenerator()
        records = generator.generate_dataset(
            count=count,
            include_fakes=include_fakes,
            include_duplicates=include_duplicates,
            include_shifted=include_shifted
        )
        
        return Response({
            'status': 'success',
            'message': f'Generated {len(records)} test records',
            'data': records
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def clean_data(request):
    """Clean and validate company data"""
    records = request.data.get('records', [])
    remove_duplicates = request.data.get('remove_duplicates', True)
    
    try:
        if not records:
            return Response({
                'status': 'error',
                'message': 'No records provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cleaner = DataCleaner()
        cleaned_records, skipped = cleaner.clean_dataset(records, remove_duplicates=remove_duplicates)
        stats = cleaner.get_summary_stats(cleaned_records)
        
        return Response({
            'status': 'success',
            'message': f'Cleaned {len(cleaned_records)} records',
            'data': cleaned_records,
            'stats': stats,
            'skipped_count': len(skipped)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def export_to_excel(request):
    """Export cleaned data to Excel file"""
    records = request.data.get('records', [])
    filename = request.data.get('filename', 'cleaned_data.xlsx')
    
    try:
        if not records:
            return Response({
                'status': 'error',
                'message': 'No records provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create exports directory if it doesn't exist
        export_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        filepath = os.path.join(export_dir, filename)
        
        cleaner = DataCleaner()
        success = cleaner.export_to_excel(records, filepath)
        
        if success:
            return Response({
                'status': 'success',
                'message': f'Data exported to {filepath}',
                'filepath': filepath,
                'record_count': len(records)
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': 'Failed to export data'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def full_pipeline(request):
    """
    Complete pipeline: scrape/load -> clean -> export
    """
    source = request.data.get('source', 'test')  # 'test', 'scrape', 'upload'
    city = request.data.get('city', '')
    export_format = request.data.get('export_format', 'excel')  # 'excel', 'csv'
    
    try:
        # Step 1: Get data
        if source == 'test':
            count = request.data.get('count', 50)
            generator = TestDataGenerator()
            records = generator.generate_dataset(count=count)
            source_info = f"Generated {count} test records"
        elif source == 'scrape':
            if not city:
                return Response({
                    'status': 'error',
                    'message': 'City required for scraping'
                }, status=status.HTTP_400_BAD_REQUEST)
            records = scrape_data(city)
            source_info = f"Scraped data for {city}"
        else:
            uploaded_data = request.data.get('records', [])
            records = uploaded_data
            source_info = "Uploaded data"
        
        # Step 2: Clean data
        cleaner = DataCleaner()
        cleaned_records, skipped = cleaner.clean_dataset(records, remove_duplicates=True)
        stats = cleaner.get_summary_stats(cleaned_records)
        
        # Step 3: Export
        export_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        filename = f"{city or 'data'}_{export_format}.{'xlsx' if export_format == 'excel' else 'csv'}"
        filepath = os.path.join(export_dir, filename)
        
        if export_format == 'excel':
            export_success = cleaner.export_to_excel(cleaned_records, filepath)
        else:
            export_success = cleaner.export_to_csv(cleaned_records, filepath)
        
        if export_success:
            return Response({
                'status': 'success',
                'message': 'Pipeline completed successfully',
                'source': source_info,
                'original_count': len(records),
                'cleaned_count': len(cleaned_records),
                'skipped_count': len(skipped),
                'stats': stats,
                'export_path': filepath,
                'records': cleaned_records[:50]  # Return first 50 records for preview
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': 'Data cleaning succeeded but export failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
