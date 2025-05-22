import pandas as pd
from openpyxl.chart import LineChart, Reference
from openpyxl.utils.dataframe import dataframe_to_rows

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
    max_col = sheet.max_column
    
    chart = LineChart()
    chart.title = "Evolution du nombre de bulles"
    chart.y_axis.title = "Nombre de bulles"
    chart.x_axis.title = "Temps (s)"
    
    data = Reference(sheet, min_col=2, min_row=1, max_row=max_row)  # nb_bulles
    cats = Reference(sheet, min_col=1, min_row=2, max_row=max_row)  # frame
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    
    chart.legend = None
    
    serie = chart.series[0]
    serie.graphicalProperties.line.solidFill = "4472C4"
    serie.marker.symbol = "circle"
    serie.marker.size = 7
    serie.marker.graphicalProperties.solidFill = "4472C4"  # Intérieur du marqueur
    serie.marker.graphicalProperties.line.solidFill = "4472C4"  # Bordure du marqueur
    
    sheet.add_chart(chart, "G2")