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
                "surface_moyenne[cm²]": [],
                "ecart_type[cm²]": []
            }
        grouped_data[frame]["nb_bulles"].append(row["nb_bulles"])
        grouped_data[frame]["surface_moyenne[cm²]"].append(row["surface_moyenne[cm²]"])
        grouped_data[frame]["ecart_type[cm²]"].append(row["ecart_type[cm²]"])

    summary_rows = []
    for frame, mesures in sorted(grouped_data.items()):
        summary_rows.append({
            "frame": frame,
            "nb_bulles": sum(mesures["nb_bulles"]) / len(mesures["nb_bulles"]),
            "surface_moyenne[cm²]": sum(mesures["surface_moyenne[cm²]"]) / len(mesures["surface_moyenne[cm²]"]),
            "ecart_type[cm²]": sum(mesures["ecart_type[cm²]"]) / len(mesures["ecart_type[cm²]"]),
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

    # Sheet 3: Height data
    df3 = xls.parse(sheet_name="Hauteur - Données brutes")
    cols3 = df3.iloc[:, [1, 2, 3]].copy()
    cols3.columns = ["hmousse [mm]", "hliquide [mm]", "htotal [mm]"]

    # Sheet 7: Structure data
    df7 = xls.parse(sheet_name="Structure - Données brutes")
    cols7 = df7.iloc[:, [4, 7]].copy()
    cols7.columns = ["Rmoy [µm]", "R32 [µm]"]

    max_rows = min(len(cols3), len(cols7))
    n_frames = len(important_frames)
    max_valid = min(max_rows, n_frames)

    filtered_cols3 = cols3.iloc[:max_valid].reset_index(drop=True)
    filtered_cols3["frame"] = important_frames[:max_valid]
    filtered_cols7 = cols7.iloc[:max_valid].reset_index(drop=True)

    combined = pd.concat([filtered_cols3, filtered_cols7], axis=1)
    return combined
