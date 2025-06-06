#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: export_utils.py
Description :tility functions for summarizing and exporting video analysis results to Excel, including chart generation and merging of external Excel parameters.
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
    Generates a summary DataFrame aggregating mean values per frame across all videos.

    Args:
        data_frames (list[pd.DataFrame]): List of DataFrames containing per-video analysis data.

    Returns:
        pd.DataFrame: Summary DataFrame with averaged values per frame.
    """
    all_data = pd.concat(data_frames, ignore_index=True)
    grouped_data = {}

    for _, row in all_data.iterrows():
        frame = int(round(row["frame"]))
        if frame not in grouped_data:
            grouped_data[frame] = {
                "nb_bulles": [],
                "surface_moyenne[mm²]": [],
                "ecart_type[mm²]": []
            }
        grouped_data[frame]["nb_bulles"].append(row["nb_bulles"])
        grouped_data[frame]["surface_moyenne[mm²]"].append(row["surface_moyenne[mm²]"])
        grouped_data[frame]["ecart_type[mm²]"].append(row["ecart_type[mm²]"])

    summary_rows = []
    for frame, mesures in sorted(grouped_data.items()):
        summary_rows.append({
            "frame": frame,
            "nb_bulles": sum(mesures["nb_bulles"]) / len(mesures["nb_bulles"]),
            "surface_moyenne[mm²]": sum(mesures["surface_moyenne[mm²]"]) / len(mesures["surface_moyenne[mm²]"]),
            "ecart_type[mm²]": sum(mesures["ecart_type[mm²]"]) / len(mesures["ecart_type[mm²]"]),
        })

    return pd.DataFrame(summary_rows)


def add_summary_chart(workbook, worksheet_name: str = "Résumé"):
    """
    Adds a line chart to the given worksheet showing bubble count evolution over frames.

    Args:
        workbook (openpyxl.Workbook): The workbook where the chart will be added.
        worksheet_name (str, optional): Name of the worksheet containing the data. Defaults to "Résumé".
    """
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


def extract_relevant_excel_data(excel_path: str, important_frames: list[int]) -> pd.DataFrame:
    """
    Extracts and merges data from specific sheets of an Excel file for selected frame indices.

    Args:
        excel_path (str): Path to the Excel file.
        important_frames (list[int]): List of frame indices to extract.

    Returns:
        pd.DataFrame: Merged DataFrame containing filtered data from both sheets.
    """
    xls = pd.ExcelFile(excel_path)
    
    df3 = xls.parse(sheet_name="Hauteur - Données brutes")
    df7 = xls.parse(sheet_name="Structure - Données brutes")

    # Récupération des colonnes utiles avec noms explicites
    df3 = df3[["t [s]", "hmousse [mm]", "hliquide [mm]", "htotal [mm]"]]
    df7 = df7[["Rmoy [µm]", "R32 [µm]"]]

    selected_df3 = df3.iloc[important_frames].reset_index(drop=True)
    selected_df7 = df7.iloc[important_frames].reset_index(drop=True)

    # Création de la colonne 'frame'
    selected_df3.insert(0, "frame", important_frames)

    # Fusion finale
    final_df = pd.concat([selected_df3, selected_df7], axis=1)

    return final_df
