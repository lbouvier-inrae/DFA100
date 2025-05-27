#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: export_model.py
Author: Maxime Gosselin
Contact: maximeg391@gmail.com
License: MIT License
"""
import pandas as pd
from pathlib import Path
from processing.export_utils import generate_summary_sheet, add_summary_chart

class ExportModel:
    def export_results(self, output_filename, data_frames, param_excels):
        output_path = Path("assets/results") / output_filename
        summary_df = generate_summary_sheet(data_frames)

        with pd.ExcelWriter(output_path) as writer:
            summary_df.to_excel(writer, sheet_name="Résumé", index=False)
            for i, df in enumerate(data_frames):
                df.to_excel(writer, sheet_name=f"video{i+1}", index=False)
                if param_excels[i] is not None:
                    param_excels[i].to_excel(writer, sheet_name=f"video{i+1}_param", index=False)
            add_summary_chart(writer.book)

        return str(output_path)
