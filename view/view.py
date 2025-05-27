#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: view.py
Author: Maxime Gosselin
Contact: maximeg391@gmail.com
License: MIT License
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QLineEdit, QHBoxLayout, QDateEdit, QListWidget, QSpinBox
)
from PyQt5.QtCore import Qt, QDate

class VideoAnalyzerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bubble Video Analyzer")
        self.setMinimumSize(600, 400)

        self.on_add_video = None
        self.on_remove_video = None
        self.on_attach_excel = None
        self.on_analyze = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # videos list
        self.video_list = QListWidget()
        layout.addWidget(self.video_list)

        button_layout = QHBoxLayout()
        self.add_video_btn = QPushButton("Add video")
        self.add_video_btn.clicked.connect(self.add_video)
        button_layout.addWidget(self.add_video_btn)

        self.remove_video_btn = QPushButton("Remove selected video")
        self.remove_video_btn.clicked.connect(self.remove_selected)
        button_layout.addWidget(self.remove_video_btn)

        self.add_excel_btn = QPushButton("Excel file of selected video")
        self.add_excel_btn.clicked.connect(self.attach_excel)
        button_layout.addWidget(self.add_excel_btn)

        layout.addLayout(button_layout)
        
        # Experiment name label and input
        exp_name_label = QLabel("Experiment name :")
        self.exp_name_input = QLineEdit()
        self.exp_name_input.setPlaceholderText("Experiment name")
        self.exp_name_input.textChanged.connect(self.update_filename)
        layout.addWidget(exp_name_label)
        layout.addWidget(self.exp_name_input)
        
        # Date selector
        date_label = QLabel("Experiment date :")
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.dateChanged.connect(self.update_filename)
        layout.addWidget(date_label)
        layout.addWidget(self.date_input)

        # Scale label and input
        scale_label = QLabel("Scale (px/cm) :")
        self.scale_input = QLineEdit()
        self.scale_input.setPlaceholderText("e.g., 1000")
        layout.addWidget(scale_label)
        layout.addWidget(self.scale_input)

        # Step label and input
        step_label = QLabel("Step (1 = analyse every frame):")
        self.step_input = QSpinBox()
        self.step_input.setMinimum(1)
        self.step_input.setValue(1)
        layout.addWidget(step_label)
        layout.addWidget(self.step_input)

        # Output filename label and input
        filename_label = QLabel("Output .xlsx file name")
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("Output filename")
        layout.addWidget(filename_label)
        layout.addWidget(self.filename_input)

        # Analysis button
        self.analyze_btn = QPushButton("Start analysis")
        self.analyze_btn.clicked.connect(self.start_analysis)
        layout.addWidget(self.analyze_btn)

        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def add_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Videos (*.avi *.mp4)")
        if path and self.on_add_video:
            text = self.on_add_video(path)
            if text:
                self.video_list.addItem(text)

    def remove_selected(self):
        row = self.video_list.currentRow()
        if row >= 0 and self.on_remove_video and self.on_remove_video(row):
            self.video_list.takeItem(row)

    def attach_excel(self):
        row = self.video_list.currentRow()
        if row >= 0:
            path, _ = QFileDialog.getOpenFileName(self, "Select Excel", "", "Excel Files (*.xls *.xlsx)")
            if path and self.on_attach_excel:
                updated_text = self.on_attach_excel(row, path)
                if updated_text:
                    self.video_list.item(row).setText(updated_text)

    def update_filename(self):
        name = self.exp_name_input.text().strip()
        date = self.date_input.date().toString("yyyy_MM_dd")
        if name:
            self.filename_input.setText(f"{name}_{date}.xlsx")

    def start_analysis(self):
        try:
            scale = float(self.scale_input.text())
            step = self.step_input.value()
            filename = self.filename_input.text().strip()
            if not filename.endswith(".xlsx"):
                raise ValueError("Output filename must end with .xlsx")

            if self.on_analyze:
                path = self.on_analyze(step, scale, filename)
                self.status_label.setText(f"Saved to: {path}")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
