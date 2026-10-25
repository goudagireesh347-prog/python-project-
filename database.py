"""
Database configuration and ORM models for Smart Food Waste Reduction System.
Uses Flask-SQLAlchemy with SQLite database.
"""
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    organization_type = db.Column(db.String(50), default='Household') # Household, Restaurant, Hotel, College Canteen, Supermarket
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    food_items = db.relationship('FoodItem', backref='owner', lazy=True, cascade='all, delete-orphan')
    waste_records = db.relationship('WasteRecord', backref='owner', lazy=True, cascade='all, delete-orphan')
    donations = db.relationship('Donation', backref='owner', lazy=True, cascade='all, delete-orphan')
    predictions = db.relationship('PredictionRecord', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class FoodItem(db.Model):
    __tablename__ = 'food_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    food_name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(60), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(30), default='kg') # kg, g, liters, items, packets, servings
    purchase_date = db.Column(db.Date, nullable=False, default=date.today)
    expiry_date = db.Column(db.Date, nullable=False)
    storage_type = db.Column(db.String(50), default='Refrigerator') # Refrigerator, Freezer, Pantry / Room Temp
    purchase_cost = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default='active') # active, consumed, wasted, donated
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    @property
    def days_remaining(self):
        """Calculates days left before expiry relative to today."""
        if not self.expiry_date:
            return 0
        delta = (self.expiry_date - date.today()).days
        return delta

    @property
    def expiry_status(self):
        """
        Calculates category color status:
        - expired: days_remaining < 0 (Red)
        - expiring_soon: 0 <= days_remaining <= 3 (Yellow / Warning)
        - fresh: days_remaining > 3 (Green)
        """
        remaining = self.days_remaining
        if remaining < 0:
            return 'expired'
        elif remaining <= 3:
            return 'expiring_soon'
        else:
            return 'fresh'

    @property
    def badge_class(self):
        status = self.expiry_status
        if status == 'expired':
            return 'bg-danger'
        elif status == 'expiring_soon':
            return 'bg-warning text-dark'
        return 'bg-success'

    @property
    def status_label(self):
        status = self.expiry_status
        if status == 'expired':
            days_ago = abs(self.days_remaining)
            return f"Expired ({days_ago} day{'s' if days_ago != 1 else ''} ago)"
        elif status == 'expiring_soon':
            if self.days_remaining == 0:
                return "Expires Today!"
            elif self.days_remaining == 1:
                return "Expires Tomorrow (1 day)"
            return f"Expiring Soon ({self.days_remaining} days left)"
        else:
            return f"Fresh ({self.days_remaining} days left)"


class WasteRecord(db.Model):
    __tablename__ = 'waste_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    food_name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(60), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(30), default='kg')
    reason = db.Column(db.String(100), nullable=False) # Past Expiry Date, Spoiled / Mold, Plate Waste, Overcooked, Storage Failure, Over-purchased
    waste_date = db.Column(db.Date, nullable=False, default=date.today)
    estimated_cost = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)


class Donation(db.Model):
    __tablename__ = 'donations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    food_name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(60), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(30), default='kg')
    pickup_location = db.Column(db.String(255), nullable=False)
    storage_condition = db.Column(db.String(100), default='Properly Packed & Refrigerated')
    preparation_date = db.Column(db.Date, nullable=True, default=date.today)
    safe_deadline = db.Column(db.String(80), nullable=False) # e.g. "Tomorrow 4:00 PM" or date string
    contact_info = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(30), default='Available') # Available, Reserved, Donated, Cancelled
    recipient_name = db.Column(db.String(120), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)


class PredictionRecord(db.Model):
    __tablename__ = 'prediction_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    food_category = db.Column(db.String(60), nullable=False)
    quantity_purchased = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(30), default='kg')
    days_to_expiry = db.Column(db.Integer, nullable=False)
    storage_type = db.Column(db.String(50), nullable=False)
    household_diners = db.Column(db.Integer, default=3)
    predicted_waste_quantity = db.Column(db.Float, nullable=False)
    predicted_waste_percentage = db.Column(db.Float, nullable=False)
    waste_risk_level = db.Column(db.String(20), default='Low') # Low, Moderate, High
    recommendation = db.Column(db.Text, nullable=True)
    prediction_date = db.Column(db.DateTime, default=datetime.now)


def seed_initial_data():
    """
    Seeds initial realistic sample data for demo user and testing.
    Ensures dashboard and all pages are immediately full of rich, testable data.
    """
    # Check if demo user already exists
    demo_user = User.query.filter_by(username='demo').first()
    if not demo_user:
        demo_user = User(
            username='demo',
            email='demo@smartfoodwaste.org',
            full_name='Alex Green (Demo Kitchen)',
            organization_type='College Canteen / Household'
        )
        demo_user.set_password('demo123')
        db.session.add(demo_user)
        db.session.commit()
    
    # If user already has food items, don't re-seed
    existing_items_count = FoodItem.query.filter_by(user_id=demo_user.id).count()
    if existing_items_count > 0:
        return

    today = date.today()

    # 1. Seed Food Inventory items (spanning Fresh, Expiring Soon, Expired, and Consumed)
    sample_inventory = [
        # Fresh (days_remaining > 3)
        FoodItem(
            user_id=demo_user.id,
            food_name="Organic Brown Basmati Rice",
            category="Grains & Cereals",
            quantity=5.0,
            unit="kg",
            purchase_date=today - timedelta(days=7),
            expiry_date=today + timedelta(days=60),
            storage_type="Pantry / Room Temp",
            purchase_cost=14.50,
            status="active",
            notes="Stored in airtight container in dry pantry"
        ),
        FoodItem(
            user_id=demo_user.id,
            food_name="Whole Wheat Sandwich Bread",
            category="Bakery",
            quantity=2.0,
            unit="items",
            purchase_date=today - timedelta(days=1),
            expiry_date=today + timedelta(days=6),
            storage_type="Pantry / Room Temp",
            purchase_cost=5.00,
            status="active",
            notes="Brand new pack, keep sealed"
        ),
        FoodItem(
            user_id=demo_user.id,
            food_name="Fresh Fuji Apples",
            category="Fruits & Vegetables",
            quantity=2.5,
            unit="kg",
            purchase_date=today - timedelta(days=2),
            expiry_date=today + timedelta(days=10),
            storage_type="Refrigerator",
            purchase_cost=6.50,
            status="active",
            notes="Crisp and fresh in crisper drawer"
        ),
        FoodItem(
            user_id=demo_user.id,
            food_name="Frozen Sweet Corn & Green Peas",
            category="Fruits & Vegetables",
            quantity=1.5,
            unit="kg",
            purchase_date=today - timedelta(days=14),
            expiry_date=today + timedelta(days=120),
            storage_type="Freezer",
            purchase_cost=4.80,
            status="active",
            notes="Stored at -18°C"
        ),
        FoodItem(
            user_id=demo_user.id,
            food_name="Extra Virgin Olive Oil",
            category="Pantry & Condiments",
            quantity=1.0,
            unit="liters",
            purchase_date=today - timedelta(days=20),
            expiry_date=today + timedelta(days=200),
            storage_type="Pantry / Room Temp",
            purchase_cost=15.00,
            status="active",
            notes="Dark glass bottle away from heat"
        ),

        # Expiring Soon (0 to 3 days remaining)
        FoodItem(
            user_id=demo_user.id,
            food_name="Fresh Greek Yogurt",
            category="Dairy & Eggs",
            quantity=1.0,
            unit="kg",
            purchase_date=today - timedelta(days=6),
            expiry_date=today + timedelta(days=1),
            storage_type="Refrigerator",
            purchase_cost=4.90,
            status="active",
            notes="Recommend using in smoothies or baked parfaits today!"
        ),
        FoodItem(
            user_id=demo_user.id,
            food_name="Tender Baby Spinach",
            category="Fruits & Vegetables",
            quantity=0.5,
            unit="kg",
            purchase_date=today - timedelta(days=4),
            expiry_date=today + timedelta(days=2),
            storage_type="Refrigerator",
            purchase_cost=3.20,
            status="active",
            notes="Needs to be cooked or frozen into pesto"
        ),
        FoodItem(
            user_id=demo_user.id,
            food_name="Fresh Boneless Chicken Breast",
            category="Meat & Poultry",
            quantity=1.2,
            unit="kg",
            purchase_date=today - timedelta(days=2),
            expiry_date=today + timedelta(days=2),
            storage_type="Refrigerator",
            purchase_cost=10.50,
            status="active",
            notes="Cook tonight or move to freezer immediately"
        ),
        FoodItem(
            user_id=demo_user.id,
            food_name="Artisan Brioche Buns",
            category="Bakery",
            quantity=6.0,
            unit="items",
            purchase_date=today - timedelta(days=3),
            expiry_date=today + timedelta(days=1),
            storage_type="Pantry / Room Temp",
            purchase_cost=4.20,
            status="active",
            notes="Eligible for donation or freeze before expiry"
        ),

        # Expired (days_remaining < 0) - clearly marked unsafe
        FoodItem(
            user_id=demo_user.id,
            food_name="Whole Pasteurized Milk",
            category="Dairy & Eggs",
            quantity=1.0,
            unit="liters",
            purchase_date=today - timedelta(days=10),
            expiry_date=today - timedelta(days=2),
            storage_type="Refrigerator",
            purchase_cost=2.75,
            status="active",
            notes="Past expiry date! Excluded from donation/consumption."
        ),
        FoodItem(
            user_id=demo_user.id,
            food_name="Ripe Strawberries",
            category="Fruits & Vegetables",
            quantity=0.4,
            unit="kg",
            purchase_date=today - timedelta(days=8),
            expiry_date=today - timedelta(days=1),
            storage_type="Refrigerator",
            purchase_cost=4.00,
            status="active",
            notes="Overripe and showing decay. Must be composted/logged as waste."
        ),

        # Consumed (food saved)
        FoodItem(
            user_id=demo_user.id,
            food_name="Cheddar Cheese Block",
            category="Dairy & Eggs",
            quantity=0.6,
            unit="kg",
            purchase_date=today - timedelta(days=15),
            expiry_date=today - timedelta(days=1),
            storage_type="Refrigerator",
            purchase_cost=5.50,
            status="consumed",
            notes="Used completely before expiry!"
        ),
        FoodItem(
            user_id=demo_user.id,
            food_name="Rolled Oats (Quick Cooking)",
            category="Grains & Cereals",
            quantity=2.0,
            unit="kg",
            purchase_date=today - timedelta(days=25),
            expiry_date=today + timedelta(days=40),
            storage_type="Pantry / Room Temp",
            purchase_cost=6.00,
            status="consumed",
            notes="Fully utilized for breakfasts."
        )
    ]
    db.session.add_all(sample_inventory)

    # 2. Seed Waste Records across the past month
    sample_waste = [
        WasteRecord(
            user_id=demo_user.id,
            food_name="Leftover Vegetable Lasagna",
            category="Prepared Meals",
            quantity=0.8,
            unit="kg",
            reason="Plate Waste / Leftovers",
            waste_date=today - timedelta(days=2),
            estimated_cost=6.40,
            notes="Prepared too much for the evening dinner."
        ),
        WasteRecord(
            user_id=demo_user.id,
            food_name="Brown Bananas",
            category="Fruits & Vegetables",
            quantity=1.2,
            unit="kg",
            reason="Spoiled / Mold",
            waste_date=today - timedelta(days=5),
            estimated_cost=2.80,
            notes="Over-ripened on counter before making banana bread."
        ),
        WasteRecord(
            user_id=demo_user.id,
            food_name="Heavy Cream 500ml",
            category="Dairy & Eggs",
            quantity=0.5,
            unit="liters",
            reason="Past Expiry Date",
            waste_date=today - timedelta(days=9),
            estimated_cost=3.50,
            notes="Opened for recipe and forgotten at the back of the fridge."
        ),
        WasteRecord(
            user_id=demo_user.id,
            food_name="Sourdough Baguette",
            category="Bakery",
            quantity=2.0,
            unit="items",
            reason="Past Expiry Date",
            waste_date=today - timedelta(days=14),
            estimated_cost=5.20,
            notes="Went stale and hardened."
        ),
        WasteRecord(
            user_id=demo_user.id,
            food_name="Salmon Fillet (Burnt during grilling)",
            category="Seafood",
            quantity=0.6,
            unit="kg",
            reason="Overcooked / Burnt",
            waste_date=today - timedelta(days=19),
            estimated_cost=12.00,
            notes="Kitchen timer misconfiguration."
        ),
        WasteRecord(
            user_id=demo_user.id,
            food_name="Cottage Cheese Tub",
            category="Dairy & Eggs",
            quantity=0.4,
            unit="kg",
            reason="Storage Failure",
            waste_date=today - timedelta(days=24),
            estimated_cost=3.10,
            notes="Fridge door was left ajar overnight."
        )
    ]
    db.session.add_all(sample_waste)

    # 3. Seed Food Donations
    sample_donations = [
        Donation(
            user_id=demo_user.id,
            food_name="Fresh Farm Gala Apples (Surplus Harvest)",
            category="Fruits & Vegetables",
            quantity=10.0,
            unit="kg",
            pickup_location="Campus Dining Hall, Rear Dock Door 4",
            storage_condition="Freshly Packed in Wooden Crates (Cool & Dry)",
            preparation_date=today,
            safe_deadline=(today + timedelta(days=4)).strftime('%Y-%m-%d') + " by 6:00 PM",
            contact_info="campus-dining@university.edu | (555) 392-1084",
            status="Available",
            notes="Pristine quality surplus from local orchard partnership. Suitable for shelters or student pantry."
        ),
        Donation(
            user_id=demo_user.id,
            food_name="Unopened Whole Wheat Bagels & Dinner Rolls",
            category="Bakery",
            quantity=20.0,
            unit="items",
            pickup_location="Bistro Canteen, 45 University Ave",
            storage_condition="Commercial sealed food-grade packaging",
            preparation_date=today - timedelta(days=1),
            safe_deadline=(today + timedelta(days=2)).strftime('%Y-%m-%d') + " by 12:00 PM",
            contact_info="manager@bistro.org | (555) 748-2910",
            status="Reserved",
            recipient_name="St. Mary's Youth Shelter",
            notes="Volunteer pickup scheduled for tomorrow morning."
        ),
        Donation(
            user_id=demo_user.id,
            food_name="Assorted Canned Vegetable Soups & Beans",
            category="Canned Goods",
            quantity=18.0,
            unit="items",
            pickup_location="Community Pantry Locker #12",
            storage_condition="Room Temperature, Undented Commercial Cans",
            preparation_date=today - timedelta(days=5),
            safe_deadline="Safe until manufacturer date: 2027-12-31",
            contact_info="volunteer-rep@citypantry.org | (555) 912-4022",
            status="Donated",
            recipient_name="City Central Food Bank",
            notes="Donation completed and distributed successfully."
        )
    ]
    db.session.add_all(sample_donations)

    # 4. Seed Prediction Records
    sample_predictions = [
        PredictionRecord(
            user_id=demo_user.id,
            food_category="Fruits & Vegetables",
            quantity_purchased=6.0,
            unit="kg",
            days_to_expiry=4,
            storage_type="Refrigerator",
            household_diners=3,
            predicted_waste_quantity=1.45,
            predicted_waste_percentage=24.2,
            waste_risk_level="Moderate",
            recommendation="Consume within 3 days or blend into smoothies/soups to freeze."
        ),
        PredictionRecord(
            user_id=demo_user.id,
            food_category="Dairy & Eggs",
            quantity_purchased=3.0,
            unit="liters",
            days_to_expiry=3,
            storage_type="Refrigerator",
            household_diners=2,
            predicted_waste_quantity=1.10,
            predicted_waste_percentage=36.7,
            waste_risk_level="High",
            recommendation="Quantity exceeds expected 2-person consumption rate. Consider baking or donating surplus."
        )
    ]
    db.session.add_all(sample_predictions)

    db.session.commit()
