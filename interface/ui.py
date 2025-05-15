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
        self.setWindowTitle("Analyseur de vidéo de bulles")
        self.setMinimumSize(600, 400)
        self.excel_path = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()        
        
        # Liste des videos
        self.videos_paths = []
        
        self.video_list = QListWidget()
        layout.addWidget(self.video_list)
        
        buttons_layout = QHBoxLayout()
        self.add_video_button = QPushButton("Ajouter une vidéo")
        self.add_video_button.clicked.connect(self.add_video)
        buttons_layout.addWidget(self.add_video_button)
        
        self.remove_video_button = QPushButton("Supprimer la vidéo sélectionnée")
        self.remove_video_button.clicked.connect(self.remove_selected_video)
        buttons_layout.addWidget(self.remove_video_button)
        
        layout.addLayout(buttons_layout)
        

        # Nom de l'expérience
        self.name_experience_input = QLineEdit()
        self.name_experience_input.setPlaceholderText("Nom de l'expérience")
        self.name_experience_input.textChanged.connect(self.update_result_filename)
        self.name_experience_input.textChanged.connect(self.validate_inputs)
        layout.addWidget(QLabel("Nom de l'expérience :"))
        layout.addWidget(self.name_experience_input)

        # Sélecteur de date
        self.date_selector = QDateEdit(QDate.currentDate())
        self.date_selector.setCalendarPopup(True)
        self.date_selector.dateChanged.connect(self.update_result_filename)
        self.date_selector.dateChanged.connect(self.validate_inputs)
        layout.addWidget(QLabel("Date de l'expérience :"))
        layout.addWidget(self.date_selector)
        
        # Section pour définir l'échelle (pixels pour 1 cm)
        scale_box = QHBoxLayout()
        self.scale_label = QLabel("Échelle (px/cm) :")
        self.scale_input = QLineEdit()
        self.scale_input.setPlaceholderText("Ex: 50")
        self.scale_input.textChanged.connect(self.validate_inputs)

        scale_box.addWidget(self.scale_label)
        scale_box.addWidget(self.scale_input)
        layout.addLayout(scale_box)

        # Chargement des paramètres machine
        self.excel_button = QPushButton("Charger les paramètres machine (Excel)")
        self.excel_button.clicked.connect(self.load_excel)
        layout.addWidget(self.excel_button)

        # Input pour les images analysées par minute
        self.img_per_min_input = QLineEdit()
        self.img_per_min_input.setPlaceholderText("Exemple : 30")
        self.img_per_min_input.textChanged.connect(self.validate_inputs)
        layout.addWidget(QLabel("Images analysées par minute :"))
        layout.addWidget(self.img_per_min_input)

        # Nom du fichier résultat
        self.name_result_input = QLineEdit()
        self.name_result_input.setPlaceholderText("Nom du fichier .xlsx")
        self.name_result_input.textChanged.connect(self.validate_inputs)
        layout.addWidget(QLabel("Nom du fichier de résultat :"))
        layout.addWidget(self.name_result_input)

        # Bouton d’analyse
        self.analyze_button = QPushButton("Lancer l’analyse")
        self.analyze_button.setEnabled(False)
        self.analyze_button.clicked.connect(self.analyze_video)
        layout.addWidget(self.analyze_button)

        # Label de statut
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def load_excel(self):
        path, _ = QFileDialog.getOpenFileName(self, "Fichier Excel", "", "Excel Files (*.xlsx *.xls)")
        if path:
            self.excel_path = path
        self.validate_inputs()

    def update_result_filename(self):
        name = self.name_experience_input.text().strip()
        date_str = self.date_selector.date().toString("yyyy_MM_dd")
        if name:
            self.name_result_input.setText(f"{name}_{date_str}.xlsx")

    def validate_inputs(self):
        errors = []
        if len(self.videos_paths) == 0:
            errors.append("Aucune vidéo chargée")
        if not self.name_experience_input.text().strip():
            errors.append("Nom de l'expérience manquant")
        if not self.name_result_input.text().strip().endswith(".xlsx"):
            errors.append("Nom de fichier de résultat invalide")
        try:
            value = float(self.img_per_min_input.text())
            if value <= 0:
                errors.append("Valeur d'images/min doit être > 0")
        except ValueError:
            errors.append("Images/min doit être un nombre")
        try:
            scale = float(self.scale_input.text())
            if scale <= 0:
                errors.append("L'échelle doit être positive")
        except ValueError:
            errors.append("L'échelle doit être un nombre")

        if errors:
            self.status_label.setText("Erreur : " + "; ".join(errors))
            self.analyze_button.setEnabled(False)
        else:
            self.status_label.setText("Prêt à analyser")
            self.analyze_button.setEnabled(True)

    def analyze_video(self):
        self.status_label.setText("Analyse en cours...")
        QApplication.processEvents()

        img_per_min = float(self.img_per_min_input.text())
        fps_video = img_per_min / 60
        
        scale_text = self.scale_input.text()
        try:
            scale = float(scale_text)
        except ValueError:
            scale = 1.0
        
        data_frames = []
        for video in self.videos_paths:
            results = analyse_video(video, fps_video, scale=scale)
            data_frames.append(pd.DataFrame(results))
            
        summary_df = generate_summary_sheet(data_frames)
        
        output_path = f"assets/results/{self.name_result_input.text()}"
        with pd.ExcelWriter(output_path) as writer:
            summary_df.to_excel(writer, sheet_name="Résumé", index=False)
            for i, df in enumerate(data_frames):
                df.to_excel(writer, sheet_name=f"video{i+1}", index=False)
            if self.excel_path:
                self.add_machine_parameters(writer, self.excel_path)
            add_summary_chart(writer.book)

        self.status_label.setText("Analyse terminée")

    def add_machine_parameters(self, writer, excel_file):
        xls = pd.ExcelFile(excel_file)
        last_sheet = xls.sheet_names[-1]
        df_parameters = xls.parse(last_sheet)
        
        df_parameters.columns = ['Configuration', 'Valeur']
        
        # Ajoute l'echelle dans la feuille de configuration
        df_scale = pd.DataFrame({'Configuration':['Echelle'], 'Valeur':[self.scale_input.text() + ' [px/cm]']})
        df_parameters = pd.concat([df_parameters, df_scale])

        df_parameters.to_excel(writer, sheet_name='Paramètres machine', index=False)
    
    def add_video(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choisir une vidéo", "", "Videos (*.avi *.mp4)")
        if file_path and file_path not in self.videos_paths:
            self.videos_paths.append(file_path)
            
            data = cv2.VideoCapture(file_path)
            
            frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
            fps = data.get(cv2.CAP_PROP_FPS)
            
            seconds = round(frames / fps)
            video_time = datetime.timedelta(seconds=seconds)
            
            self.video_list.addItem(Path(file_path).name + f"(video time: {video_time})")
            self.validate_inputs()
    
    def remove_selected_video(self):
        selected = self.video_list.currentRow()
        if selected >= 0:
            self.videos_paths.pop(selected)
            self.video_list.takeItem(selected)
            self.validate_inputs()