#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: settings_view.py
Author: Maxime Gosselin
Contact: maximeg391@gmail.com
License: MIT License
"""
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QDialog, QFileDialog, QVBoxLayout, QLabel, QPushButton,
    QCheckBox, QScrollArea, QWidget, QTabWidget
)
import pandas as pd
from processing.settings_manager import load_settings, save_settings

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags()
                    ^ QtCore.Qt.WindowContextHelpButtonHint)
        
        self.setWindowTitle("Parameters")
        self.resize(600, 400)

        self.settings = load_settings()
        self.sheet_column_map = {}
        self.checkboxes = {}

        self.layout = QVBoxLayout(self)

        self.load_button = QPushButton("Select Excel File")
        self.load_button.clicked.connect(self.load_excel)
        self.layout.addWidget(self.load_button)
        
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.save_button = QPushButton("Save parameters")
        self.save_button.clicked.connect(self.save_selection)
        self.layout.addWidget(self.save_button)

    def load_excel(self):
        path, _ = QFileDialog.getOpenFileName(self, "Excel File", "", "Excel Files (*.xlsx *.xls)")
        if not path:
            return

        self.settings["reference_excel"] = path
        xls = pd.ExcelFile(path)
        self.sheet_column_map = {}
        self.checkboxes = {}

        self.tabs.clear()  # Efface les anciens onglets

        for sheet_name in xls.sheet_names:
            try:
                df = xls.parse(sheet_name, nrows=1)
            except Exception:
                continue

            # --- Scroll Area pour chaque feuille ---
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)

            inner_widget = QWidget()
            layout = QVBoxLayout(inner_widget)

            label = QLabel(f"Sheet: {sheet_name}")
            label.setStyleSheet("font-weight: bold;")
            layout.addWidget(label)

            checkbox_list = []
            saved_cols = self.settings.get("columns", {}).get(sheet_name, [])

            for col in df.columns:
                cb = QCheckBox(col)
                cb.setChecked(col in saved_cols)
                layout.addWidget(cb)
                checkbox_list.append(cb)

            self.checkboxes[sheet_name] = checkbox_list

            scroll.setWidget(inner_widget)
            self.tabs.addTab(scroll, sheet_name)




    def save_selection(self):
        selection = {}
        for sheet_name, cbs in self.checkboxes.items():
            selected_cols = [cb.text() for cb in cbs if cb.isChecked()]
            if selected_cols:
                selection[sheet_name] = selected_cols

        self.settings["columns"] = selection
        save_settings(self.settings)
        self.accept()

