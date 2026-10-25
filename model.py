"""
Machine Learning Model module for Smart Food Waste Prediction.
Uses Scikit-learn (RandomForestRegressor, StandardScaler, OneHotEncoder Pipeline).
Generates a labeled synthetic dataset in data/sample_food_data.csv if not present,
trains the model, evaluates metrics (R2, MAE, RMSE), and delivers waste predictions.
"""

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
CSV_PATH = os.path.join(DATA_DIR, 'sample_food_data.csv')
MODEL_PATH = os.path.join(DATA_DIR, 'food_waste_model.joblib')
METRICS_PATH = os.path.join(DATA_DIR, 'model_metrics.joblib')

CATEGORIES = [
    'Fruits & Vegetables',
    'Dairy & Eggs',
    'Bakery',
    'Meat & Poultry',
    'Seafood',
    'Grains & Cereals',
    'Prepared Meals',
    'Beverages',
    'Snacks'
]

STORAGE_TYPES = [
    'Refrigerator',
    'Freezer',
    'Pantry / Room Temp'
]

CONSUMPTION_PACES = [
    'Slow',
    'Moderate',
    'Fast'
]


def generate_synthetic_dataset(num_samples=1200, output_path=CSV_PATH):
    """
    Generates a realistic, clearly labelled synthetic training dataset.
    Simulates real food waste dynamics:
    - Short shelf life + high quantity + low consumers + poor storage = higher waste.
    - Freezers and fast consumption reduce waste significantly.
    """
    np.random.seed(42)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    records = []

    # Category typical parameters (base shelf life days, vulnerability factor)
    cat_props = {
        'Fruits & Vegetables': {'shelf_mean': 7, 'vuln': 0.32},
        'Dairy & Eggs': {'shelf_mean': 10, 'vuln': 0.28},
        'Bakery': {'shelf_mean': 5, 'vuln': 0.35},
        'Meat & Poultry': {'shelf_mean': 4, 'vuln': 0.25},
        'Seafood': {'shelf_mean': 3, 'vuln': 0.30},
        'Grains & Cereals': {'shelf_mean': 60, 'vuln': 0.08},
        'Prepared Meals': {'shelf_mean': 4, 'vuln': 0.33},
        'Beverages': {'shelf_mean': 14, 'vuln': 0.15},
        'Snacks': {'shelf_mean': 90, 'vuln': 0.06}
    }

    for _ in range(num_samples):
        cat = np.random.choice(CATEGORIES)
        props = cat_props[cat]

        # Quantity purchased in kg or standard units (0.5 to 10.0)
        qty_purchased = round(float(np.random.exponential(scale=2.2) + 0.5), 2)
        qty_purchased = min(qty_purchased, 15.0)

        # Shelf life in days
        shelf_life = max(1, int(np.random.normal(props['shelf_mean'], props['shelf_mean'] * 0.35)))
        
        # Days remaining before expiry (between 0 and shelf_life + 2)
        days_remaining = max(0, int(np.random.uniform(0, shelf_life + 1)))

        # Storage type
        storage = np.random.choice(STORAGE_TYPES, p=[0.55, 0.20, 0.25])

        # Household diners / Consumers
        diners = int(np.random.choice([1, 2, 3, 4, 5, 6, 8, 10], p=[0.20, 0.30, 0.25, 0.15, 0.04, 0.03, 0.02, 0.01]))

        # Consumption pace
        pace = np.random.choice(CONSUMPTION_PACES, p=[0.25, 0.55, 0.20])
        pace_factor = {'Slow': 1.35, 'Moderate': 1.0, 'Fast': 0.65}[pace]

        # Storage benefit factor
        storage_factor = {'Freezer': 0.20, 'Refrigerator': 0.85, 'Pantry / Room Temp': 1.25}[storage]
        if cat in ['Meat & Poultry', 'Seafood', 'Dairy & Eggs'] and storage == 'Pantry / Room Temp':
            storage_factor = 2.5 # Rapid spoilage if perishable food not cooled

        # Historical waste baseline for user
        hist_waste_rate = round(float(np.random.beta(2, 8)), 2)

        # Base formula for waste percentage:
        # Higher if:
        # - purchased quantity per diner is high compared to shelf life
        # - days remaining is low
        # - high vulnerability factor
        qty_per_diner = qty_purchased / max(diners, 1)
        urgency_ratio = max(0.05, (shelf_life - days_remaining) / max(shelf_life, 1))

        raw_waste_pct = (
            props['vuln'] * 0.40 +
            (qty_per_diner * 0.06) +
            (urgency_ratio * 0.25) +
            (hist_waste_rate * 0.15)
        ) * pace_factor * storage_factor

        # Add realistic noise
        noise = np.random.normal(0, 0.05)
        waste_pct = max(0.0, min(0.95, raw_waste_pct + noise))
        waste_qty = round(qty_purchased * waste_pct, 2)
        waste_pct = round(waste_pct * 100, 1)

        records.append({
            'food_category': cat,
            'quantity_purchased': qty_purchased,
            'shelf_life_days': shelf_life,
            'days_remaining': days_remaining,
            'storage_type': storage,
            'household_diners': diners,
            'consumption_pace': pace,
            'historical_waste_rate': hist_waste_rate,
            'waste_quantity_kg': waste_qty,
            'waste_percentage': waste_pct
        })

    df = pd.DataFrame(records)
    # Add metadata comments in file by saving via pandas
    df.to_csv(output_path, index=False)
    print(f"Generated synthetic dataset with {len(df)} samples at {output_path}")
    return df


def train_model(force_retrain=False):
    """
    Trains the Scikit-learn RandomForestRegressor pipeline.
    Saves trained pipeline and evaluation metrics.
    """
    if not os.path.exists(CSV_PATH):
        generate_synthetic_dataset()

    if not force_retrain and os.path.exists(MODEL_PATH) and os.path.exists(METRICS_PATH):
        try:
            pipeline = joblib.load(MODEL_PATH)
            metrics = joblib.load(METRICS_PATH)
            return pipeline, metrics
        except Exception as e:
            print(f"Warning: loading saved model failed ({e}), retraining...")

    df = pd.read_csv(CSV_PATH)

    features = [
        'food_category',
        'quantity_purchased',
        'shelf_life_days',
        'days_remaining',
        'storage_type',
        'household_diners',
        'consumption_pace',
        'historical_waste_rate'
    ]
    target = 'waste_quantity_kg'

    X = df[features]
    y = df[target]

    categorical_features = ['food_category', 'storage_type', 'consumption_pace']
    numerical_features = ['quantity_purchased', 'shelf_life_days', 'days_remaining', 'household_diners', 'historical_waste_rate']

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
        ]
    )

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42))
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    r2 = round(float(r2_score(y_test, y_pred)), 4)
    mae = round(float(mean_absolute_error(y_test, y_pred)), 4)
    rmse = round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 4)

    metrics = {
        'r2_score': r2,
        'mae': mae,
        'rmse': rmse,
        'test_samples': len(y_test),
        'total_samples': len(df),
        'model_name': 'Random Forest Regressor (Scikit-learn)'
    }

    joblib.dump(pipeline, MODEL_PATH)
    joblib.dump(metrics, METRICS_PATH)
    print(f"Model successfully trained and saved: R2={r2}, MAE={mae}, RMSE={rmse}")
    return pipeline, metrics


def get_model_and_metrics():
    """Returns the loaded model pipeline and evaluation metrics."""
    return train_model(force_retrain=False)


def generate_recommendations(category, waste_pct, days_remaining, storage_type, quantity):
    """
    Generates intelligent, actionable waste reduction recommendations
    tailored to category, storage method, and urgency.
    """
    tips = []

    # Urgency & Expiry based
    if days_remaining <= 1:
        tips.append("⚡ Immediate Action: Use this item within 24 hours or freeze it immediately.")
    elif days_remaining <= 3:
        tips.append("📅 Expiry Nearing: Plan dinner recipes featuring this item over the next 2-3 days.")

    # Category-specific guidance
    if category == 'Fruits & Vegetables':
        tips.append("🍏 Storage Tip: Keep ethylene producers (apples, bananas) separate from leafy greens to avoid premature rotting.")
        if waste_pct > 25:
            tips.append("🥗 Surplus Strategy: Blend ripe vegetables into pasta sauces or freeze chopped fruits for morning smoothies.")
    elif category == 'Dairy & Eggs':
        tips.append("🥛 Temperature Tip: Store dairy on the middle refrigerator shelf (3°C - 4°C), avoiding the warm door shelves.")
        if waste_pct > 20:
            tips.append("🧀 Preservation: Hard cheeses can be grated and frozen; yogurts can be baked into scones or parfaits.")
    elif category == 'Bakery':
        tips.append("🍞 Bread Care: Never store fresh bread in the fridge (it stales faster). Slice and freeze in airtight bags.")
        if waste_pct > 25:
            tips.append("🥖 Repurpose: Turn dry bread into homemade croutons, breadcrumbs, or French toast.")
    elif category == 'Meat & Poultry':
        tips.append("🍗 Cold Chain: If not cooking within 48 hours of purchase, portion into freezer bags and freeze at -18°C.")
    elif category == 'Seafood':
        tips.append("🐟 Critical Freshness: Prepare within 24 hours of purchase or pack tightly in freezer-safe vacuum bags.")
    elif category in ['Grains & Cereals', 'Pantry & Condiments']:
        tips.append("🌾 Dry Storage: Keep in airtight glass or BPA-free containers with moisture absorbers away from sunlight.")
    elif category == 'Prepared Meals':
        tips.append("🍲 Portion Control: Divide bulk meals into single-serving airtight containers and label with the date.")

    # Storage-specific guidance
    if storage_type == 'Pantry / Room Temp' and category in ['Dairy & Eggs', 'Meat & Poultry', 'Seafood']:
        tips.append("⚠️ Critical Warning: Highly perishable items must not be kept at room temperature. Refrigerate immediately!")
    elif storage_type != 'Freezer' and waste_pct >= 35:
        tips.append("❄️ Freezing Option: Freezing this item before the expiry date will extend its safe shelf life by 2-6 months.")

    # Quantity-based guidance
    if quantity > 4.0:
        tips.append("🛒 Purchasing Habit: Consider buying smaller batch sizes or shopping twice a week to reduce volume risk.")

    # Donation recommendation
    if days_remaining >= 2 and waste_pct >= 30:
        tips.append("🤝 Donation Opportunity: List surplus quantity on the Food Donation Board before quality degrades.")

    return tips


def predict_food_waste(
    food_category,
    quantity_purchased,
    shelf_life_days,
    days_remaining,
    storage_type='Refrigerator',
    household_diners=3,
    consumption_pace='Moderate',
    historical_waste_rate=0.15
):
    """
    Predicts the expected waste quantity and percentage for a given food item.
    Returns:
    - predicted_waste_qty: float (in kg/units)
    - predicted_waste_pct: float (in %)
    - risk_level: 'Low', 'Moderate', or 'High'
    - risk_badge: Bootstrap badge class
    - saved_qty: estimated consumable quantity
    - recommendations: list of actionable advice strings
    - metrics: model evaluation statistics
    """
    pipeline, metrics = get_model_and_metrics()

    # Input dataframe matching training features
    input_df = pd.DataFrame([{
        'food_category': food_category,
        'quantity_purchased': float(quantity_purchased),
        'shelf_life_days': int(shelf_life_days),
        'days_remaining': int(days_remaining),
        'storage_type': storage_type,
        'household_diners': int(household_diners),
        'consumption_pace': consumption_pace,
        'historical_waste_rate': float(historical_waste_rate)
    }])

    try:
        raw_pred = pipeline.predict(input_df)[0]
    except Exception as e:
        # Safe mathematical fallback if pipeline fails
        print(f"Prediction fallback due to error: {e}")
        urgency = max(0.1, (shelf_life_days - days_remaining) / max(shelf_life_days, 1))
        raw_pred = float(quantity_purchased) * 0.25 * urgency

    pred_qty = max(0.0, min(float(quantity_purchased), float(raw_pred)))
    pred_qty = round(pred_qty, 2)

    if float(quantity_purchased) > 0:
        pred_pct = round((pred_qty / float(quantity_purchased)) * 100, 1)
    else:
        pred_pct = 0.0

    # Risk level categorization
    if pred_pct < 15.0:
        risk_level = 'Low Risk'
        risk_badge = 'bg-success'
    elif pred_pct < 35.0:
        risk_level = 'Moderate Risk'
        risk_badge = 'bg-warning text-dark'
    else:
        risk_level = 'High Risk'
        risk_badge = 'bg-danger'

    saved_qty = round(max(0.0, float(quantity_purchased) - pred_qty), 2)
    recommendations = generate_recommendations(food_category, pred_pct, days_remaining, storage_type, float(quantity_purchased))

    return {
        'predicted_waste_quantity': pred_qty,
        'predicted_waste_percentage': pred_pct,
        'saved_quantity': saved_qty,
        'risk_level': risk_level,
        'risk_badge': risk_badge,
        'recommendations': recommendations,
        'model_metrics': metrics,
        'is_synthetic_model': True,
        'disclaimer': "Machine learning estimate generated using a trained Random Forest Regressor on experimental and synthetic benchmark distributions. Actual spoilage depends on specific storage temperature, packaging, and handling."
    }
