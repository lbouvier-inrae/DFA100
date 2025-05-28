#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: export_model.py
Description: This module defines the ExportModel class used to export video analysis results to an Excel file in the Bubble Video Analyzer application.
Author: Maxime Gosselin
Contact: maximeg391@gmail.com
License: MIT License
"""

import pandas as pd
from pathlib import Path
from processing.export_utils import generate_summary_sheet, add_summary_chart


class ExportModel:
    """
    Handles the export of analysis data to Excel files.

    This includes writing a summary sheet, per-video analysis sheets,
    optional parameter sheets, and generating a chart.
    """

    def export_results(self, output_filename, data_frames, param_excels):
        """
        Export all video analysis data and optional configuration parameters to an Excel file.

        The Excel file will contain:
        - A summary sheet aggregating key results from all videos.
        - One sheet per video with detailed frame-by-frame analysis.
        - Optionally, one sheet per video with attached Excel parameter values.
        - A summary chart added to the Excel workbook.

        Args:
            output_filename (str): Name of the resulting Excel file (must end with .xlsx).
            data_frames (List[pd.DataFrame]): List of dataframes containing per-video analysis results.
            param_excels (List[pd.DataFrame or None]): List of dataframes with configuration parameters
                or None for videos without attached Excel files.

        Returns:
            str: Path to the saved Excel file as a string.
        """
        output_path = Path("assets/results") / output_filename
        summary_df = generate_summary_sheet(data_frames)

        with pd.ExcelWriter(output_path) as writer:
            # Write the global summary sheet
            summary_df.to_excel(writer, sheet_name="Résumé", index=False)

            for i, df in enumerate(data_frames):
                # Write analysis data for each video
                df.to_excel(writer, sheet_name=f"video{i+1}", index=False)

                # Write associated parameter sheet, if available
                if param_excels[i] is not None:
                    param_excels[i].to_excel(writer, sheet_name=f"video{i+1}_param", index=False)

            # Add a summary chart to the workbook
            add_summary_chart(writer.book)

        return str(output_path)
