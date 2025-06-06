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
    QLineEdit, QHBoxLayout, QDateEdit, QListWidget, QSpinBox,
    QDialog
)
from PyQt5.QtCore import QDate, QPoint, Qt
from PyQt5.QtGui import QPixmap, QPainter, QPen
import math

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

        self.video_list = QListWidget()
        layout.addWidget(self.video_list)

        # Buttons layout
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

        # Experiment name
        name_layout = QHBoxLayout()
        name_label = QLabel("Experiment name :")
        self.exp_name_input = QLineEdit()
        self.exp_name_input.setPlaceholderText("Experiment name")
        self.exp_name_input.textChanged.connect(self.update_filename)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.exp_name_input)
        layout.addLayout(name_layout)

        # Date input
        date_layout = QHBoxLayout()
        date_label = QLabel("Experiment date :")
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.dateChanged.connect(self.update_filename)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)
        layout.addLayout(date_layout)

        # Scale input
        scale_layout = QHBoxLayout()
        scale_label = QLabel("Scale (px/mm) :")
        self.scale_display = QLineEdit()
        
        self.select_scale_btn = QPushButton("Définir à partir d'une image")
        self.select_scale_btn.clicked.connect(self.open_scale_selector)
        
        scale_layout.addWidget(scale_label)
        scale_layout.addWidget(self.scale_display)
        scale_layout.addWidget(self.select_scale_btn)
        layout.addLayout(scale_layout)

        # Step input
        step_layout = QHBoxLayout()
        step_label = QLabel("Step (1 = analyse every frame):")
        self.step_input = QSpinBox()
        self.step_input.setMinimum(1)
        self.step_input.setValue(1)
        step_layout.addWidget(step_label)
        step_layout.addWidget(self.step_input)
        layout.addLayout(step_layout)

        # Agitation input
        agitation_layout = QHBoxLayout()
        agitation_label = QLabel("Agitation (frames to ignore at start):")
        self.agitation_input = QSpinBox()
        self.agitation_input.setMinimum(0)
        self.agitation_input.setValue(0)
        agitation_layout.addWidget(agitation_label)
        agitation_layout.addWidget(self.agitation_input)
        layout.addLayout(agitation_layout)

        # Filename
        file_layout = QHBoxLayout()
        filename_label = QLabel("Output .xlsx file name:")
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("Output filename")
        file_layout.addWidget(filename_label)
        file_layout.addWidget(self.filename_input)
        layout.addLayout(file_layout)

        # Analyze button
        self.analyze_btn = QPushButton("Start analysis")
        self.analyze_btn.clicked.connect(self.start_analysis)
        layout.addWidget(self.analyze_btn)

        # Status label
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
            scale = float(self.scale_display.text())
            step = self.step_input.value()
            agitation = self.agitation_input.value()
            filename = self.filename_input.text().strip()
            if not filename.endswith(".xlsx"):
                raise ValueError("Output filename must end with .xlsx")

            if self.on_analyze:
                path = self.on_analyze(step, scale, filename, agitation)
                self.status_label.setText(f"Saved to: {path}")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
    
    def open_scale_selector(self):
        class ScaleDialog(QDialog):
            def __init__(dialog_self):
                super().__init__()
                dialog_self.setWindowTitle("Cliquez sur deux points distants de 1 mm")

                dialog_self.label = QLabel()
                dialog_self.layout = QVBoxLayout()
                dialog_self.layout.addWidget(dialog_self.label)
                dialog_self.setLayout(dialog_self.layout)

                file_path, _ = QFileDialog.getOpenFileName(self, "Choisir une image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
                if not file_path:
                    dialog_self.reject()
                    return

                dialog_self.pixmap = QPixmap(file_path)
                dialog_self.original = dialog_self.pixmap.copy()
                dialog_self.label.setPixmap(dialog_self.pixmap)
                dialog_self.label.mousePressEvent = dialog_self.record_click

                dialog_self.points = []

            def record_click(dialog_self, event):
                if len(dialog_self.points) < 2:
                    pos = event.pos()
                    dialog_self.points.append(QPoint(pos))

                    pm = dialog_self.original.copy()
                    painter = QPainter(pm)
                    pen = QPen(Qt.red, 3)
                    painter.setPen(pen)

                    for pt in dialog_self.points:
                        painter.drawEllipse(pt, 4, 4)

                    if len(dialog_self.points) == 2:
                        painter.drawLine(dialog_self.points[0], dialog_self.points[1])
                    painter.end()

                    dialog_self.label.setPixmap(pm)

                    if len(dialog_self.points) == 2:
                        dx = dialog_self.points[1].x() - dialog_self.points[0].x()
                        dy = dialog_self.points[1].y() - dialog_self.points[0].y()
                        px_distance = math.hypot(dx, dy)

                        self.scale_display.setText(f"{px_distance:.2f}")  # px/mm
                        dialog_self.accept()

        dialog = ScaleDialog()
        dialog.exec_()
