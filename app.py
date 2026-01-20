import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objs as go
import json
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import os
import sys

# Add current directory to path so imports work if modules exist
sys.path.append(os.getcwd())

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash messages

# --- MOCK DATA GENERATOR ---
def generate_mock_data(date_1, date_2):
    """Generates a mock df_All_MKD_Spreads if the real function fails."""
    # Create a date range between date_1 and date_2
    # For demo, let's just create a few dates
    dates = pd.date_range(start=date_1, end=date_2, freq='D')
    if len(dates) > 50: # Limit points for clearer mock graph
        dates = pd.date_range(start=date_1, end=date_2, periods=50)
        
    data = []
    
    products = ['Prod1', 'Prod2']
    maturities = ['1D', '2W', '1M', '3M', '6M', '1Y', '5Y', '10Y']
    
    # Columns to simulate
    spread_cols = [
        'ESTR', 'EURx1M', 'EURx3M', 'EURx6M', 'EURx1Y',
        'ESTRx1M', 'ESTRx3M', 'ESTRx6M', 'ESTRx1Y',
        '3Mx1M', '3Mx3M', '3Mx6M', '3Mx1Y', '3MxESTR', '3MxESTRS'
    ]
    
    for prod in products:
        for date in dates:
            for mat in maturities:
                row = {
                    'Prod': prod,
                    'Dates': date,
                    'Maturite': mat,
                    'MaturiteMonth': 1, # Mock value
                    'End_Date': date    # Mock value
                }
                
                # Random data for spreads
                for col in spread_cols:
                    base = 0.5 if 'ESTR' in col else 0.8
                    row[col] = base + np.random.normal(0, 0.1)
                
                data.append(row)
                
    df = pd.DataFrame(data)
    return df

# --- WRAPPER FOR Risque_Couvert ---
def get_risk_coverage_data(start_date, end_date):
    """
    Attempts to call the real Risque_Couvert function.
    Falls back to mock data if imports or execution fails.
    """
    try:
        # Try to import just-in-time so we handle missing modules gracefully
        from Risque_Couvert import Risque_Couvert
        
        # The real function takes date strings? Logic says yes based on usage
        print(f"Calling real Risque_Couvert with {start_date}, {end_date}")
        result = Risque_Couvert(start_date, end_date)
        print("hello")
        # Result is a tuple, df_All_MKD_Spreads is the first element
        df_All_MKD_Spreads = result[0]
        return df_All_MKD_Spreads, False # False = not mocked
        
    except (ImportError, ModuleNotFoundError, Exception) as e:
        print(f"Could not run Risque_Couvert: {e}")
        print("Switching to MOCK data mode.")
        mock_df = generate_mock_data(start_date, end_date)
        return mock_df, True # True = mocked

# --- ROUTES ---

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/visualize', methods=['POST'])
def visualize():
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    
    # Conversion des dates pour Risque_Couvert
    try:
        fmt_start = datetime.strptime(start_date_str, '%Y-%m-%d').strftime('%d/%m/%Y')
        fmt_end = datetime.strptime(end_date_str, '%Y-%m-%d').strftime('%d/%m/%Y')
    except:
        fmt_start, fmt_end = start_date_str, end_date_str

    df, is_mock = get_risk_coverage_data(fmt_start, fmt_end)
    
    # Important : S'assurer que les colonnes numériques sont bien au format float
    # et trier par MaturiteMonth pour que la courbe soit correcte (1D -> 30Y)
    df = df.sort_values('MaturiteMonth')

    # Colonnes de spreads disponibles
    spread_cols = [c for c in df.columns if c not in ['Prod', 'Dates', 'Maturite', 'MaturiteMonth', 'End_Date']]
    
    # Envoyer le dataframe complet en JSON pour le filtrage JS
    df_json = df.to_json(orient='records')
    
    return render_template('dashboard.html', 
                           df_json=df_json, 
                           spread_cols=spread_cols, 
                           prods=df['Prod'].unique().tolist(),
                           is_mock=is_mock, 
                           start=fmt_start, 
                           end=fmt_end)
if __name__ == '__main__':
    app.run(debug=True)
