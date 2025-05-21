import sys
import os
import cv2
import datetime
from pathlib import Path
import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QFileDialog, QLineEdit, QHBoxLayout,
    QDateEdit, QListWidget
)
from PySide6.QtCore import Qt, QDate
from processing.video_analyser import analyse_video
from processing.export_utils import (generate_summary_sheet, add_summary_chart)


class VideoAnalyzerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bubble Video Analyzer")
        self.setMinimumSize(600, 400)

        self.videos_data = {}
        self.excel_path = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Liste des videos
        self.video_list = QListWidget()
        layout.addWidget(self.video_list)

        buttons_layout = QHBoxLayout()
        self.add_video_button = QPushButton("Add a video")
        self.add_video_button.clicked.connect(self.add_video)
        buttons_layout.addWidget(self.add_video_button)

        self.remove_video_button = QPushButton("Remove selected video")
        self.remove_video_button.clicked.connect(self.remove_selected_video)
        buttons_layout.addWidget(self.remove_video_button)

        self.add_excel_button = QPushButton("Excel file of selected video")
        self.add_excel_button.clicked.connect(self.add_excel_file)
        buttons_layout.addWidget(self.add_excel_button)

        layout.addLayout(buttons_layout)

        self.name_experience_input = QLineEdit()
        self.name_experience_input.setPlaceholderText("Experiment name")
        self.name_experience_input.textChanged.connect(self.update_result_filename)
        self.name_experience_input.textChanged.connect(self.validate_inputs)
        layout.addWidget(QLabel("Experiment name :"))
        layout.addWidget(self.name_experience_input)

        # Sélecteur de date
        self.date_selector = QDateEdit(QDate.currentDate())
        self.date_selector.setCalendarPopup(True)
        self.date_selector.dateChanged.connect(self.update_result_filename)
        self.date_selector.dateChanged.connect(self.validate_inputs)
        layout.addWidget(QLabel("Experiment date :"))
        layout.addWidget(self.date_selector)

        scale_box = QHBoxLayout()
        self.scale_label = QLabel("Scale (px/cm) :")
        self.scale_input = QLineEdit()
        self.scale_input.setPlaceholderText("e.g., 50")
        self.scale_input.textChanged.connect(self.validate_inputs)

        scale_box.addWidget(self.scale_label)
        scale_box.addWidget(self.scale_input)
        layout.addLayout(scale_box)

        # Chargement des paramètres machine
        self.excel_button = QPushButton("Load machine settings (Excel)")
        self.excel_button.clicked.connect(self.load_excel)
        layout.addWidget(self.excel_button)

        # Input pour les images analysées par minute
        self.img_per_min_input = QLineEdit()
        self.img_per_min_input.setPlaceholderText("e.g., 30")
        self.img_per_min_input.textChanged.connect(self.validate_inputs)
        layout.addWidget(QLabel("Images analyzed per minute :"))
        layout.addWidget(self.img_per_min_input)

        # Nom du fichier résultat
        self.name_result_input = QLineEdit()
        self.name_result_input.setPlaceholderText("Output .xlsx file name")
        self.name_result_input.textChanged.connect(self.validate_inputs)
        layout.addWidget(QLabel("Output file name :"))
        layout.addWidget(self.name_result_input)

        # Bouton d’analyse
        self.analyze_button = QPushButton("Start analysis")
        self.analyze_button.setEnabled(False)
        self.analyze_button.clicked.connect(self.analyze_video)
        layout.addWidget(self.analyze_button)

        # Label de statut
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def load_excel(self):
        path, _ = QFileDialog.getOpenFileName(self, "Excel File", "", "Excel Files (*.xlsx *.xls)")
        if path:
            self.excel_path = path

    def update_result_filename(self):
        name = self.name_experience_input.text().strip()
        date_str = self.date_selector.date().toString("yyyy_MM_dd")
        if name:
            self.name_result_input.setText(f"{name}_{date_str}.xlsx")

    def validate_inputs(self):
        errors = []
        if not self.videos_data:
            errors.append("No video loaded")
        if not self.name_experience_input.text().strip():
            errors.append("Missing experiment name")
        if not (self.name_result_input.text().strip().endswith(".xlsx") or self.name_result_input.text().strip().endswith(".xls")):
            errors.append("Invalid output file name")
        try:
            value = float(self.img_per_min_input.text())
            if value <= 0:
                errors.append("Images/min must be > 0")
        except ValueError:
            errors.append("Images/min must be a number")
        try:
            scale = float(self.scale_input.text())
            if scale <= 0:
                errors.append("Scale must be > 0")
        except ValueError:
            errors.append("Scale must be a number")

        if errors:
            self.status_label.setText("Error : " + "; ".join(errors))
            self.analyze_button.setEnabled(False)
        else:
            self.status_label.setText("Ready to analyze")
            self.analyze_button.setEnabled(True)

    def analyze_video(self):
        self.status_label.setText("Analyzing...")
        QApplication.processEvents()

        img_per_min = float(self.img_per_min_input.text())
        fps_video = img_per_min / 60

        try:
            scale = float(self.scale_input.text())
        except ValueError:
            scale = 1.0

        data_frames = []
        ordered_excels = []

        for video_path, info in self.videos_data.items():
            results = analyse_video(video_path, fps_video, scale=scale)
            df = pd.DataFrame(results)
            data_frames.append(df)

            if info["excel"]:
                try:
                    xls = pd.ExcelFile(info["excel"])
                    last_sheet = xls.sheet_names[-1]
                    df_param = xls.parse(last_sheet)
                    df_param.columns = ['Configuration', 'Value']
                    ordered_excels.append(df_param)
                except Exception as e:
                    ordered_excels.append(None)
            else:
                ordered_excels.append(None)

        summary_df = generate_summary_sheet(data_frames)
        output_path = f"assets/results/{self.name_result_input.text()}"

        with pd.ExcelWriter(output_path) as writer:
            summary_df.to_excel(writer, sheet_name="Résumé", index=False)
            for i, df in enumerate(data_frames):
                df.to_excel(writer, sheet_name=f"video{i+1}", index=False)
                if ordered_excels[i] is not None:
                    ordered_excels[i].to_excel(writer, sheet_name=f"video{i+1}_param", index=False)

            if self.excel_path:
                self.add_machine_parameters(writer, self.excel_path)

            add_summary_chart(writer.book)

        self.status_label.setText("Analysis completed")

    def add_machine_parameters(self, writer, excel_file):
        xls = pd.ExcelFile(excel_file)
        last_sheet = xls.sheet_names[-1]
        df_parameters = xls.parse(last_sheet)
        
        df_parameters.columns = ['Configuration', 'Value']
        df_scale = pd.DataFrame({'Configuration': ['Echelle'], 'Value': [self.scale_input.text() + ' [px/cm]']})
        df_parameters = pd.concat([df_parameters, df_scale])
        df_parameters.to_excel(writer, sheet_name='Paramètres machine', index=False)

    def add_video(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose a video", "", "Videos (*.avi *.mp4)")
        if file_path and file_path not in self.videos_data:
            cap = cv2.VideoCapture(file_path)
            frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            self.videos_data[file_path] = {"excel": None, "frame": frames}
            self.video_list.addItem(f"{Path(file_path).name} (frames: {frames}) - excel not loaded")
            self.validate_inputs()

    def remove_selected_video(self):
        selected = self.video_list.currentRow()
        if selected >= 0:
            video_path = list(self.videos_data.keys())[selected]
            self.videos_data.pop(video_path)
            self.video_list.takeItem(selected)
            self.validate_inputs()

    def add_excel_file(self):
        selected = self.video_list.currentRow()
        if selected >= 0:
            video_path = list(self.videos_data.keys())[selected]
            path, _ = QFileDialog.getOpenFileName(self, "Fichier Excel", "", "Excel Files (*.xlsx *.xls)")
            if path:
                self.videos_data[video_path]["excel"] = path
                frames = self.videos_data[video_path]["frame"]
                file_name = Path(video_path).name
                self.video_list.item(selected).setText(f"{file_name} (frames: {frames}) - file loaded")
