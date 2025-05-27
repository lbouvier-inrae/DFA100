#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: controller.py
Author: Maxime Gosselin
Contact: maximeg391@gmail.com
License: MIT License
"""
from model.video_model import VideoModel
from model.export_model import ExportModel
from pathlib import Path

class VideoAnalyzerController:
    def __init__(self, view):
        self.view = view
        self.model = VideoModel()
        self.exporter = ExportModel()

        self.connect_signals()

    def connect_signals(self):
        self.view.on_add_video = self.handle_add_video
        self.view.on_remove_video = self.handle_remove_video
        self.view.on_attach_excel = self.handle_attach_excel
        self.view.on_analyze = self.handle_analyze

    def handle_add_video(self, file_path):
        frames = self.model.add_video(file_path)
        if frames is not None:
            return f"{Path(file_path).name} (frames: {frames}) - excel not loaded"
        return None

    def handle_remove_video(self, index):
        keys = list(self.model.videos_data.keys())
        if 0 <= index < len(keys):
            self.model.remove_video(keys[index])
            return True
        return False

    def handle_attach_excel(self, index, excel_path):
        keys = list(self.model.videos_data.keys())
        if 0 <= index < len(keys):
            self.model.attach_excel(keys[index], excel_path)
            frames = self.model.videos_data[keys[index]]["frame"]
            return f"{Path(keys[index]).name} (frames: {frames}) - file loaded"
        return None

    def handle_analyze(self, step, scale, output_filename):
        data_frames, param_excels = self.model.analyze_all(step, scale)
        output_path = self.exporter.export_results(output_filename, data_frames, param_excels)
        return output_path
