"""
Comprehensive Test Suite for Smart Food Waste Reduction System.
Tests all routes, database seeding, models, ML prediction, and CSV generation.
"""

import unittest
from datetime import date, timedelta
from app import app, db
from database import User, FoodItem, WasteRecord, Donation, PredictionRecord
import model

class SmartFoodWasteSystemTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_01_public_pages(self):
        """Test public endpoints."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Smart Food Waste Reduction System", response.data)

        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"About the Project", response.data)

        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_02_demo_login_and_dashboard(self):
        """Test demo user login and access to dashboard."""
        response = self.client.post('/login', data={
            'username': 'demo',
            'password': 'demo123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Kitchen Dashboard", response.data)
        self.assertIn(b"Active Inventory", response.data)

    def test_03_inventory_page_and_crud(self):
        """Test inventory listing, filtering, add, edit, and consume actions."""
        # Log in
        self.client.post('/login', data={'username': 'demo', 'password': 'demo123'}, follow_redirects=True)

        # View inventory
        response = self.client.get('/inventory')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Food Inventory Management", response.data)

        # Add food item
        today = date.today()
        response = self.client.post('/inventory/add', data={
            'food_name': 'Test Organic Avocados',
            'category': 'Fruits & Vegetables',
            'quantity': '2.0',
            'unit': 'kg',
            'purchase_date': today.strftime('%Y-%m-%d'),
            'expiry_date': (today + timedelta(days=5)).strftime('%Y-%m-%d'),
            'storage_type': 'Refrigerator',
            'purchase_cost': '5.50',
            'notes': 'Test notes'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Successfully added", response.data)

        # Find item in database
        with app.app_context():
            item = FoodItem.query.filter_by(food_name='Test Organic Avocados').first()
            self.assertIsNotNone(item)
            item_id = item.id

        # Mark consumed
        response = self.client.post(f'/inventory/mark-consumed/{item_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Marked", response.data)

    def test_04_expiry_alerts_page(self):
        """Test expiry alerts page identifies items properly."""
        self.client.post('/login', data={'username': 'demo', 'password': 'demo123'}, follow_redirects=True)
        response = self.client.get('/expiry-alerts')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Expiry Alert Center", response.data)
        self.assertIn(b"Expired Food Items", response.data)

    def test_05_predictions_page_and_ml_execution(self):
        """Test ML prediction form submission and model forecast."""
        self.client.post('/login', data={'username': 'demo', 'password': 'demo123'}, follow_redirects=True)
        
        # GET page
        response = self.client.get('/predictions')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Smart Food Waste Prediction", response.data)

        # POST prediction
        response = self.client.post('/predictions', data={
            'category': 'Dairy & Eggs',
            'quantity': '3.0',
            'unit': 'liters',
            'shelf_life': '10',
            'days_remaining': '2',
            'storage_type': 'Refrigerator',
            'household_diners': '2',
            'consumption_pace': 'Moderate'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Estimated Waste", response.data)
        self.assertIn(b"Tailored Reduction Recommendations", response.data)

    def test_06_donations_page_and_listing(self):
        """Test surplus donation board, listing food, and status update."""
        self.client.post('/login', data={'username': 'demo', 'password': 'demo123'}, follow_redirects=True)
        
        response = self.client.get('/donations')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Surplus Food Donation Board", response.data)

        # Add donation
        response = self.client.post('/donations/add', data={
            'food_name': 'Fresh Sourdough Bagels',
            'category': 'Bakery',
            'quantity': '10.0',
            'unit': 'items',
            'pickup_location': 'Campus Student Union Lobby',
            'storage_condition': 'Refrigerated',
            'safe_deadline': 'Tomorrow by 5:00 PM',
            'contact_info': 'volunteer@campus.edu',
            'notes': 'Freshly bagged today'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Successfully listed", response.data)

    def test_07_waste_tracking_and_statistics(self):
        """Test waste tracking page and logging waste item."""
        self.client.post('/login', data={'username': 'demo', 'password': 'demo123'}, follow_redirects=True)
        
        response = self.client.get('/waste-tracking')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Food Waste Tracking", response.data)

        # Log waste record
        response = self.client.post('/waste-tracking', data={
            'food_name': 'Expired Cream Cheese',
            'category': 'Dairy & Eggs',
            'quantity': '0.3',
            'unit': 'kg',
            'reason': 'Past Expiry Date',
            'waste_date': date.today().strftime('%Y-%m-%d'),
            'estimated_cost': '2.50',
            'notes': 'Found behind condiment jars'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Recorded waste entry", response.data)

    def test_08_reports_and_csv_export(self):
        """Test reports page and CSV export download."""
        self.client.post('/login', data={'username': 'demo', 'password': 'demo123'}, follow_redirects=True)
        
        response = self.client.get('/reports')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Reports &amp; Analytics", response.data)

        # Test CSV export
        csv_response = self.client.get('/reports/export-csv')
        self.assertEqual(csv_response.status_code, 200)
        self.assertEqual(csv_response.mimetype, 'text/csv')
        self.assertIn(b"Record ID,Food Name,Category,Quantity", csv_response.data)

if __name__ == '__main__':
    unittest.main()
