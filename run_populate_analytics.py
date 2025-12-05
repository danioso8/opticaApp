import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, r'd:\ESCRITORIO\OpticaApp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now import and run the populate function
from populate_analytics_data import populate_analytics_data

populate_analytics_data()
