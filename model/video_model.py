#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: video_model.py
Author: Maxime Gosselin
Contact: maximeg391@gmail.com
License: MIT License
"""
import cv2
import pandas as pd
from pathlib import Path
from processing.video_analyser import analyse_video

class VideoModel:
    def __init__(self):
        self.videos_data = {}

    def add_video(self, file_path):
        if file_path not in self.videos_data:
            cap = cv2.VideoCapture(file_path)
            frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            self.videos_data[file_path] = {"excel": None, "frame": frames}
            return frames
        return None

    def remove_video(self, file_path):
        if file_path in self.videos_data:
            del self.videos_data[file_path]

    def attach_excel(self, file_path, excel_path):
        if file_path in self.videos_data:
            self.videos_data[file_path]["excel"] = excel_path

    def analyze_all(self, step, scale, agitation):
        data_frames = []
        param_excels = []

        for video_path, info in self.videos_data.items():
            results = analyse_video(video_path, step=step, scale=scale, agitation=agitation)
            df = pd.DataFrame(results)
            data_frames.append(df)

            excel_path = info.get("excel")
            if excel_path:
                try:
                    xls = pd.ExcelFile(excel_path)
                    last_sheet = xls.sheet_names[-1]
                    df_param = xls.parse(last_sheet)
                    df_param.columns = ['Configuration', 'Value']
                    param_excels.append(df_param)
                except Exception:
                    param_excels.append(None)
            else:
                param_excels.append(None)

        return data_frames, param_excels
