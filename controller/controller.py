#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: controller.py
Description: This module implements the controller logic for the Bubble Video Analyzer GUI application.It connects user interactions from the view to underlying data processing and exporting logic.
Author: Maxime Gosselin
Contact: maximeg391@gmail.com
License: MIT License
"""

from model.video_model import VideoModel
from model.export_model import ExportModel
from pathlib import Path

 
class VideoAnalyzerController:
    """
    Controller for the Bubble Video Analyzer application.

    Connects the GUI view with the underlying video processing and export models.
    Handles user actions such as adding videos, attaching Excel files, and launching analysis.
    """

    def __init__(self, view):
        """
        Initialize the controller with the given view.

        Args:
            view (VideoAnalyzerUI): The graphical user interface instance.
        """
        self.view = view
        self.model = VideoModel()
        self.exporter = ExportModel()

        self.connect_signals()

    def connect_signals(self):
        """
        Connect UI callbacks to controller methods.
        """
        self.view.on_add_video = self.handle_add_video
        self.view.on_remove_video = self.handle_remove_video
        self.view.on_attach_excel = self.handle_attach_excel
        self.view.on_analyze = self.handle_analyze

    def handle_add_video(self, file_path):
        """
        Handle the action of adding a video file.

        Args:
            file_path (str): Path to the selected video file.

        Returns:
            str: A display string with the video name and frame count, or None on failure.
        """
        frames = self.model.add_video(file_path)
        if frames is not None:
            return f"{Path(file_path).name} (frames: {frames}) - excel not loaded"
        return None

    def handle_remove_video(self, index):
        """
        Handle the action of removing a selected video.

        Args:
            index (int): Index of the video in the list.

        Returns:
            bool: True if the video was successfully removed, False otherwise.
        """
        keys = list(self.model.videos_data.keys())
        if 0 <= index < len(keys):
            self.model.remove_video(keys[index])
            return True
        return False

    def handle_attach_excel(self, index, excel_path):
        """
        Handle the action of attaching an Excel file to a selected video.

        Args:
            index (int): Index of the selected video.
            excel_path (str): Path to the Excel file to attach.

        Returns:
            str: Updated display string with video and Excel status, or None on failure.
        """
        keys = list(self.model.videos_data.keys())
        if 0 <= index < len(keys):
            self.model.attach_excel(keys[index], excel_path)
            frames = self.model.videos_data[keys[index]]["frame"]
            return f"{Path(keys[index]).name} (frames: {frames}) - file loaded"
        return None

    def handle_analyze(self, step, scale, output_filename, agitation):
        """
        Handle the action of starting the video analysis.

        Args:
            step (int): Frame step interval for analysis.
            scale (float): Pixel-to-centimeter conversion scale.
            output_filename (str): Name of the output Excel file.
            agitation (int): Number of initial frames to ignore.

        Returns:
            str: Path to the generated Excel file.
        """
        data_frames, param_excels = self.model.analyze_all(step, scale, agitation)
        output_path = self.exporter.export_results(output_filename, data_frames, param_excels)
        return output_path
