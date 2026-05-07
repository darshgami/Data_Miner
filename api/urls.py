from django.urls import path
from .views import (
    search_data, 
    generate_test_data, 
    clean_data, 
    export_to_excel, 
    full_pipeline
)

urlpatterns = [
    path('search/', search_data, name='search_data'),
    path('test-data/', generate_test_data, name='generate_test_data'),
    path('clean/', clean_data, name='clean_data'),
    path('export/', export_to_excel, name='export_to_excel'),
    path('pipeline/', full_pipeline, name='full_pipeline'),
]
