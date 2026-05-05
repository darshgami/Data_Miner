import csv
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters
from .models import Contact
from .serializers import ContactSerializer
from .scraper import deep_scrape_profile

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .scraper import scrape_data

@api_view(['POST'])
def search_data(request):
    city = request.data.get("city", "")
    pincode = request.data.get("pincode", "")
    
    query = f"{city} {pincode}".strip()
    data = scrape_data(query)

    return Response(data)

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all().order_by('-created_at')
    serializer_class = ContactSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['company_name', 'url', 'email', 'phone_number', 'city', 'pincode']

    @action(detail=False, methods=['post'])
    def extract(self, request):
        urls_data = request.data.get('urls', [])
        city = request.data.get('city', '')
        pincode = request.data.get('pincode', '')
        
        extracted_contacts = []
        
        for item in urls_data:
            url = item.get('url')
            company_name = item.get('company_name', 'Unknown')
            
            if url:
                # Perform deep scrape
                scrape_data = deep_scrape_profile(url)
                
                contact, created = Contact.objects.update_or_create(
                    url=url,
                    defaults={
                        'company_name': company_name,
                        'email': scrape_data['email'],
                        'phone_number': scrape_data['phone_number'],
                        'source_site': scrape_data['source_site'],
                        'city': city,
                        'pincode': pincode
                    }
                )
                serializer = self.get_serializer(contact)
                extracted_contacts.append(serializer.data)

        return Response({'success': True, 'data': extracted_contacts})

    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="contacts.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(['ID', 'Company Name', 'URL', 'Email', 'Phone Number', 'City', 'Pincode', 'Source Site'])

        for contact in queryset:
            writer.writerow([
                contact.id,
                contact.company_name,
                contact.url,
                contact.email,
                contact.phone_number,
                contact.city,
                contact.pincode,
                contact.source_site
            ])

        return response
