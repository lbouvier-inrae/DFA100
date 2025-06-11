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
from processing.settings_manager import load_settings


def generate_summary_sheet(data_frames: list[pd.DataFrame]) -> pd.DataFrame:
    """
    Generates a summary DataFrame aggregating mean values per frame across all videos.

    Args:
        data_frames (list[pd.DataFrame]): List of DataFrames containing per-video analysis data.

    Returns:
        pd.DataFrame: Summary DataFrame with averaged values per frame.
    """
    all_data = pd.concat(data_frames, ignore_index=True)
    grouped = all_data.groupby("frame")

    # Colonnes par défaut
    default_cols = ["nb_bulles", "surface_moyenne[mm²]", "ecart_type[mm²]"]
    summary_dict = {"frame": []}
    
    for col in default_cols:
        summary_dict[col] = []

    # Colonnes supplémentaires (paramètres Excel)
    extra_cols = [col for col in all_data.columns if col not in default_cols + ["frame"]]
    for col in extra_cols:
        summary_dict[col] = []

    for frame, group in grouped:
        summary_dict["frame"].append(frame)
        for col in default_cols + extra_cols:
            summary_dict[col].append(group[col].mean())

    return pd.DataFrame(summary_dict)


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
    settings = load_settings()
    selected_columns = settings.get("columns", {})

    xls = pd.ExcelFile(excel_path)
    final_frames_df = []

    for sheet_name, columns in selected_columns.items():
        if sheet_name not in xls.sheet_names:
            continue

        try:
            df = xls.parse(sheet_name)
            selected_df = df[columns].iloc[important_frames].reset_index(drop=True)

            # Ajouter la colonne "frame" uniquement sur la première feuille traitée
            if not final_frames_df:
                selected_df.insert(0, "frame", important_frames)

            final_frames_df.append(selected_df)

        except Exception as e:
            print(f"Erreur lors du traitement de la feuille {sheet_name}: {e}")

    if not final_frames_df:
        raise ValueError("Aucune donnée extraite depuis le fichier Excel.")

    final_df = pd.concat(final_frames_df, axis=1)
    return final_df
