import pandas as pd
import plotly
import plotly.express as px
import json
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash, Response, stream_with_context
from datetime import datetime
from flask import Response, stream_with_context, request
import os
import sys
import time

# Ajout du dossier courant pour les imports
sys.path.append(os.getcwd())

app = Flask(__name__)
app.secret_key = 'supersecretkey'
from Risque_Couvert import Risque_Couvert


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/visualize', methods=['POST'])
def visualize():
    # 1. Récupération des dates depuis le formulaire
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    
    # if not start_date_str or not end_date_str:
    #     flash("Veuillez entrer les deux dates.", "error")
    #     return redirect(url_for('index'))

    # 2. Conversion au format dd/mm/yyyy pour votre fonction Risque_Couvert
    try:
        dt_start = datetime.strptime(start_date_str, '%Y-%m-%d')
        dt_end = datetime.strptime(end_date_str, '%Y-%m-%d')
        fmt_start = dt_start.strftime('%d/%m/%Y')
        fmt_end = dt_end.strftime('%d/%m/%Y')
    except ValueError:
        fmt_start = start_date_str
        fmt_end = end_date_str

    # 3. Appel de Risque_Couvert (qui retourne les 4 dataframes)
    try:
        df_spreads, tcd_m1, tcd_m2, tcd_explain = Risque_Couvert(fmt_start, fmt_end)
    except Exception as e:
        flash(f"Erreur lors du calcul : {str(e)}", "error")
        return redirect(url_for('index'))


    # 4. Préparation des tableaux HTML pour le Dashboard
    tables_html = {
        "m1": tcd_m1.to_html(classes="min-w-full divide-y divide-gray-700 text-sm", index=False),
        "m2": tcd_m2.to_html(classes="min-w-full divide-y divide-gray-700 text-sm", index=False),
        "explain": tcd_explain.to_html(classes="min-w-full divide-y divide-gray-700 text-sm", index=False)
    }

    # 5. Préparation des données JSON pour les graphiques
    tcd_json = {
        "m1": tcd_m1.to_json(orient='split'),
        "m2": tcd_m2.to_json(orient='split'),
        "explain": tcd_explain.to_json(orient='split')
    }

    # 6. Colonnes de spreads pour le menu déroulant
    exclude = ['Prod', 'Dates', 'Maturite', 'MaturiteMonth', 'End_Date']
    spread_cols = [c for c in df_spreads.columns if c not in exclude]

    return render_template('dashboard.html', 
                           df_json=df_spreads.to_json(orient='records'),
                           spread_cols=spread_cols,
                           prods=df_spreads['Prod'].unique().tolist(),
                           tables_html=tables_html,
                           tcd_json=tcd_json,
                           start=fmt_start, 
                           end=fmt_end)






@app.route('/stream-steps')
def stream_steps():
    # On récupère les dates pour confirmer le lancement
    start = request.args.get('start_date', 'N/A')
    end = request.args.get('end_date', 'N/A')

    def generate():
        # Liste des étapes réelles de votre fonction Risque_Couvert
        etapes = [
            f"Analyse du Risque Couvert...",
            "Etape 01 : Traitement des MKD_Spreads...",
            "Etape 02 : Pivotement du All_MKD_Spreads...",
            "Etape 03 : Chargement de DETAIL_POUR_DRM...",
            "Etape 04 : Construction du Perimetre_and_Whopper...",
            "Etape 05 : GroupBy sur Perimetre_and_Whopper...",
            "Etape 06 : Construction de DETAIL_POUR_COMPTA...",
            "Etape 07 : Calcul de Whopper_explain...",
            "Etape 08 : GroupBy sur Whopper_explain...",
            "Etape 09 : Calcul de Comparaison_Explain...",
            "Etape 10 : Calcul des TCDs finaux...",
            "Etape 11 : Finalisation des graphiques..."
        ]

        for etape in etapes:
            time.sleep(2)  # On laisse le temps à l'utilisateur de lire
            yield f"data: {etape}\n\n"
        
        time.sleep(2)
        # Message CRITIQUE pour que le JavaScript sache qu'il faut rediriger
        yield "data: FINISH\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')


if __name__ == '__main__':
    # threaded=True est crucial pour que le streaming fonctionne
    app.run(debug=True, threaded=True)