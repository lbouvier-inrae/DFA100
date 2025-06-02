#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: video_model.py
Description:This module defines the VideoModel class used to manage video files, their associated metadata, and perform analysis in the Bubble Video Analyzer application.
Author: Maxime Gosselin
Contact: maximeg391@gmail.com
License: MIT License
"""

import cv2
import pandas as pd
from pathlib import Path
from processing.video_analyser import analyse_video
from processing.export_utils import extract_relevant_excel_data


class VideoModel:
    """
    Manages video files and their associated data for analysis.

    This class stores metadata for loaded videos, allows attaching Excel files,
    and triggers the analysis pipeline across all loaded videos.
    """

    def __init__(self):
        """Initialize an empty video model."""
        self.videos_data = {}

    def add_video(self, file_path):
        """
        Add a video to the model if not already present.

        Uses OpenCV to retrieve the number of frames in the video and stores this metadata.

        Args:
            file_path (str): Path to the video file.

        Returns:
            int or None: Number of frames in the video if added, None if already present.
        """
        if file_path not in self.videos_data:
            cap = cv2.VideoCapture(file_path)
            frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            self.videos_data[file_path] = {"excel": None, "frame": frames}
            return frames
        return None

    def remove_video(self, file_path):
        """
        Remove a video from the model.

        Args:
            file_path (str): Path to the video file to remove.
        """
        if file_path in self.videos_data:
            del self.videos_data[file_path]

    def attach_excel(self, file_path, excel_path):
        """
        Attach an Excel file to a video for later data enrichment.

        Args:
            file_path (str): Path to the video file.
            excel_path (str): Path to the Excel file.
        """
        if file_path in self.videos_data:
            self.videos_data[file_path]["excel"] = excel_path

    def analyze_all(self, step, scale, agitation):
        """
        Analyze all loaded videos and optionally merge Excel data.

        For each video:
        - Analyze the video using `analyse_video`.
        - If an Excel file is attached, enrich results using `extract_relevant_excel_data`.
        - Extract configuration parameters from the last sheet of the Excel file if available.

        Args:
            step (int): Interval between analyzed frames (1 = every frame).
            scale (float): Pixel to centimeter conversion factor.
            agitation (int): Number of frames to skip at the beginning.

        Returns:
            tuple:
                - List[pd.DataFrame]: One DataFrame per video with the analysis results.
                - List[pd.DataFrame or None]: Corresponding configuration parameters from Excel, or None if unavailable.
        """
        data_frames = []
        param_excels = []

        for video_path, info in self.videos_data.items():
            results = analyse_video(video_path, step=step, scale=scale, agitation=agitation)
            frames = [r["frame"] for r in results]
            df = pd.DataFrame(results)

            excel_path = info.get("excel")
            if excel_path:
                try:
                    # Merge with relevant Excel data
                    excel_data = extract_relevant_excel_data(excel_path, frames)
                    df = pd.merge(df, excel_data, on="frame")

                    # Extract configuration parameters from the last sheet
                    xls = pd.ExcelFile(excel_path)
                    last_sheet = xls.sheet_names[-1]
                    df_param = xls.parse(last_sheet)
                    df_param.columns = ['Configuration', 'Value']
                    param_excels.append(df_param)
                except Exception as e:
                    print(e)
                    param_excels.append(None)
            else:
                param_excels.append(None)

            data_frames.append(df)
        return data_frames, param_excels
