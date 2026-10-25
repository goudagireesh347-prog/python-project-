# Smart Food Waste Reduction System Using Python

A complete, responsive, full-stack Python Flask web application designed to reduce food loss across households, restaurants, hotels, college canteens, and supermarkets.

The system features real-time pantry inventory monitoring, automated 3-tier expiry alerts, an integrated Scikit-learn Machine Learning waste prediction engine, a food donation bridge to connect edible surplus food with shelters, waste cause diagnostics, and interactive analytics with CSV export.

---

## 🌟 Key Features

1. **User Authentication & Privacy**
   - Secure registration, login, and logout with Werkzeug password hashing.
   - User-isolated private inventory and waste analytics.
   - Pre-loaded **Demo Account** (`demo` / `demo123`) for instant testing.

2. **Real-Time Food Inventory Management**
   - Track food name, category, quantity, measurement unit, purchase date, expiry date, storage location, and cost.
   - Dynamic 3-tier freshness classification:
     - 🟢 **Fresh:** Days remaining > 3.
     - 🟡 **Expiring Soon:** 0 to 3 days remaining (prompts immediate recipe usage or donation).
     - 🔴 **Expired:** Days remaining < 0 (flagged unsafe; strictly excluded from consumption & donation).
   - Filter by category, search by name, or filter by freshness status.

3. **Expiry Date Alert System**
   - Automated detection of items expiring within 3 days.
   - Prominent notification badges on the top navigation bar and dashboard.
   - Smart kitchen recipes, storage optimization tips, and freeze recommendations.
   - Strict safety guardrails: expired items are distinctly labeled and cannot be donated or marked as safe food.

4. **Smart Food Waste Prediction (Machine Learning)**
   - Powered by Scikit-learn using a `RandomForestRegressor` pipeline.
   - Features evaluated: food category, quantity, shelf life, days to expiry, storage type, diners/consumers, and consumption pace.
   - Evaluates test metrics ($R^2$, MAE, RMSE) and provides transparent benchmark disclosures.
   - Outputs predicted waste volume (kg), waste risk percentage, and actionable mitigation strategies.

5. **Surplus Food Donation Board**
   - Allows users to list surplus edible food for shelters and food pantries.
   - Details: item name, quantity, pickup location, safe-use deadline, storage condition, and contact info.
   - Real-time status management: `Available`, `Reserved`, and `Donated`.
   - Built-in food safety filter: expired items cannot be submitted for donation.

6. **Food Waste Tracking & Cost Diagnostics**
   - Record food name, category, quantity, primary cause (Spoiled/Mold, Past Expiry, Plate Waste, Overcooked, Storage Failure, Over-purchased), date, and cost.
   - Daily, weekly, and monthly waste loss summaries.

7. **Reports & Analytics (Chart.js + CSV Export)**
   - Total food purchased, consumed/saved, wasted, and monetary loss.
   - Interactive charts:
     - Monthly waste trend (Line chart)
     - Waste by category (Doughnut chart)
     - Waste by reason (Bar chart)
   - One-click **Export Report (CSV)** for bookkeeping, audits, or sustainability compliance.

---

## 🛠️ Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript (ES6), Bootstrap 5.3, Bootstrap Icons
- **Backend:** Python 3, Flask 3
- **Database:** SQLite with Flask-SQLAlchemy ORM
- **Data Analysis:** Pandas, NumPy
- **Machine Learning:** Scikit-learn (`RandomForestRegressor`, `ColumnTransformer`, `StandardScaler`, `OneHotEncoder`, `joblib`)
- **Visual Charts:** Chart.js 4.4
- **Security:** Werkzeug password hashing, session management, CSRF & SQL injection protections

---

## 📁 Project Folder Structure

```text
smart_food_waste_system/
│
├── app.py                      # Main Flask application and routing
├── database.py                 # SQLite ORM models and initial data seeder
├── model.py                    # Scikit-learn ML pipeline and prediction engine
├── requirements.txt            # Python dependencies
├── README.md                   # Installation and user guide
│
├── data/
│   ├── sample_food_data.csv    # Benchmark synthetic dataset (1,200 rows)
│   ├── food_waste_model.joblib # Trained Random Forest model pipeline
│   └── model_metrics.joblib    # Evaluation metrics (R2, MAE, RMSE)
│
├── instance/
│   └── food_waste.db           # SQLite database
│
├── static/
│   ├── css/
│   │   └── style.css           # Eco green & light orange responsive styling
│   ├── js/
│   │   └── script.js           # Client filters, modals, and auto-dismiss alerts
│   └── images/
│
└── templates/
    ├── base.html               # Base layout with navbar alerts & footer
    ├── index.html              # Landing home page
    ├── register.html           # User registration
    ├── login.html              # Login with demo quick-fill
    ├── dashboard.html          # Interactive KPI dashboard & charts
    ├── inventory.html          # Inventory management & search
    ├── add_food.html           # Add new food item form
    ├── edit_food.html          # Edit item details
    ├── expiry_alerts.html      # Expiry alerts & recipes center
    ├── predictions.html        # ML waste forecast & metrics
    ├── donations.html          # Surplus food donation board
    ├── waste_tracking.html     # Waste logging & daily/weekly stats
    ├── reports.html            # Analytics, Chart.js & CSV export
    └── about.html              # Architecture, UN SDGs & sector guidance
```

---

## 🚀 How to Run the Project (Windows Instructions)

Follow these step-by-step instructions to run the application on a Windows computer:

### Step 1: Open the Project in Visual Studio Code
1. Launch **Visual Studio Code** (or PyCharm).
2. Click **File > Open Folder...** and select the `smart_food_waste_system` directory:
   ```text
   C:\Users\<YourUsername>\.gemini\antigravity\scratch\smart_food_waste_system
   ```

### Step 2: Open the Terminal
Open the integrated terminal in VS Code:
- Press `` Ctrl + ` `` (Control + Backtick) or go to **Terminal > New Terminal**.
- Ensure you are in the PowerShell terminal.

### Step 3: Create a Virtual Environment
Run the following command:
```powershell
python -m venv venv
```

### Step 4: Activate the Virtual Environment
Activate the virtual environment in Windows PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

> **Note for PowerShell execution policy error:**
> If Windows blocks activating the script with an execution policy error, run:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> .\venv\Scripts\Activate.ps1
> ```

### Step 5: Install the Dependencies
Install all required packages from `requirements.txt`:
```powershell
pip install -r requirements.txt
```

### Step 6: Start the Application
Run the Flask server:
```powershell
python app.py
```

Upon launch, the application will:
1. Automatically create the SQLite database in `instance/food_waste.db`.
2. Automatically seed the **Demo Account** and initial realistic inventory, waste records, and donations.
3. Automatically generate the synthetic training dataset and train the Scikit-learn Random Forest model.

### Step 7: Open the Application in Your Browser
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🔑 Demo Account Credentials

For quick testing without creating a new account:
- **Username:** `demo`
- **Password:** `demo123`

You can also click the **"Fill Demo"** button on the Login page to automatically fill these credentials.

---

## 🔍 Troubleshooting Guide

### 1. Missing Packages or Import Errors
If you see `ModuleNotFoundError: No module named 'flask'` (or `sklearn`, `pandas`):
- Ensure your virtual environment is activated (you should see `(venv)` in the terminal prompt).
- Run:
  ```powershell
  pip install -r requirements.txt
  ```

### 2. Port Conflict (Port 5000 Already in Use)
If port 5000 is occupied by another process:
- In `app.py`, change the last line:
  ```python
  app.run(debug=True, host='127.0.0.1', port=5001)
  ```
- Or run Flask directly on port 5001:
  ```powershell
  python -c "import app; app.app.run(port=5001)"
  ```
- Access the app at `http://127.0.0.1:5001`.

### 3. Database Reset / Re-seed
If you ever want to reset all test data back to default:
- Delete the `instance/food_waste.db` file.
- Restart `python app.py`. The database will be cleanly re-initialized and re-seeded.

---

## 🌍 UN Sustainable Development Goals (SDGs)

This application supports:
- **SDG 12: Responsible Consumption and Production** (Target 12.3: Halving per capita food waste by 2030).
- **SDG 2: Zero Hunger** (Facilitating safe surplus food donations to community pantries and shelters).

---

## 📄 License
Open source and educational project created for sustainability and academic excellence.
