#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: export_utils.py
Author: Maxime Gosselin
Contact: maximeg391@gmail.com
License: MIT License
"""
import pandas as pd
from openpyxl.chart.axis import ChartLines
from openpyxl.chart import LineChart, Reference
from openpyxl.chart.layout import Layout, ManualLayout

def generate_summary_sheet(data_frames: list[pd.DataFrame]) -> pd.DataFrame:
    """
    Regroupe tous les résultats par temps (en secondes)
    et calcule les moyennes pour chaque seconde.

    Args:
        data_frames (list): Liste de DataFrames contenant les résultats des vidéos.

    Returns:
        pd.DataFrame: Tableau des moyennes par temps.
    """
    # Fusionner toutes les données
    all_data = pd.concat(data_frames, ignore_index=True)

    # Créer un dictionnaire pour stocker les données par temps
    grouped_data = {}

    for _, row in all_data.iterrows():
        temps = int(round(row["frame"]))
        if temps not in grouped_data:
            grouped_data[temps] = {
                "nb_bulles": [],
                "surface_moyenne[cm²]": [],
                "ecart_type[cm²]": []
            }
        grouped_data[temps]["nb_bulles"].append(row["nb_bulles"])
        grouped_data[temps]["surface_moyenne[cm²]"].append(row["surface_moyenne[cm²]"])
        grouped_data[temps]["ecart_type[cm²]"].append(row["ecart_type[cm²]"])

    # Calculer les moyennes pour chaque temps
    summary_rows = []
    for temps, mesures in sorted(grouped_data.items()):
        summary_rows.append({
            "frame": temps,
            "nb_bulles": sum(mesures["nb_bulles"]) / len(mesures["nb_bulles"]),
            "surface_moyenne[cm²]": sum(mesures["surface_moyenne[cm²]"]) / len(mesures["surface_moyenne[cm²]"]),
            "ecart_type[cm²]": sum(mesures["ecart_type[cm²]"]) / len(mesures["ecart_type[cm²]"]),
        })

    return pd.DataFrame(summary_rows)

def add_summary_chart(workbook, worksheet_name="Résumé"):
    sheet = workbook[worksheet_name]
    max_row = sheet.max_row

    chart = LineChart()
    chart.title = "Evolution du nombre de bulles"
    chart.style = 2
    chart.y_axis.title = "Nombre de bulles"
    chart.x_axis.title = "Image"
    
    chart.y_axis.majorGridlines = ChartLines()
    chart.x_axis.majorGridlines = None

    data = Reference(sheet, min_col=2, min_row=1, max_row=max_row)
    cats = Reference(sheet, min_col=1, min_row=2, max_row=max_row)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.legend = None

    serie = chart.series[0]
    serie.smooth = True
    serie.graphicalProperties.line.solidFill = "4472C4"
    serie.marker.symbol = "none"

    chart.layout = Layout(
        manualLayout=ManualLayout(
            x=0.01,
            y=0.02,
            h=0.80,
            w=0.85,
        )
    )

    sheet.add_chart(chart, "G2")