import sys
import os
from datetime import datetime
from pathlib import Path
import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QFileDialog, QLineEdit, QHBoxLayout,
    QDateEdit
)
from PySide6.QtCore import Qt, QDate
from processing.video_analyser import analyse_video


class VideoAnalyzerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analyseur de vidéo de bulles")
        self.setMinimumSize(600, 400)
        self.excel_path = None
        self.file_path = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Bouton pour charger une vidéo
        self.load_button = QPushButton("Charger une vidéo")
        self.load_button.clicked.connect(self.load_video)
        layout.addWidget(self.load_button)

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

    def load_video(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Choisir une vidéo", "", "Vidéos (*.avi *.mp4)")
        if self.file_path:
            stat = os.stat(self.file_path)
            self.date_selector.setDate(datetime.fromtimestamp(stat.st_mtime))
            self.name_experience_input.setText(Path(self.file_path).stem)
        self.validate_inputs()

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
        if not self.file_path:
            errors.append("Vidéo non chargée")
        if not self.name_experience_input.text().strip():
            errors.append("Nom de l'expérience manquant")
        if not self.name_result_input.text().strip().endswith(".xlsx"):
            errors.append("Nom de fichier de résultat invalide")
        if not self.excel_path:
            errors.append("Fichier Excel non chargé")
        try:
            val = float(self.img_per_min_input.text())
            if val <= 0:
                errors.append("Valeur d'images/min doit être > 0")
        except ValueError:
            errors.append("Images/min doit être un nombre")

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

        results = analyse_video(self.file_path, fps_video)
        df = pd.DataFrame(results)

        output_path = f"assets/results/{self.name_result_input.text()}"
        df.to_excel(output_path, index=False)

        if self.excel_path:
            self.ajouter_parametres_machine(output_path, self.excel_path)

        self.status_label.setText("Analyse terminée")

    def ajouter_parametres_machine(self, fichier_resultat, fichier_excel):
        xls = pd.ExcelFile(fichier_excel)
        last_sheet = xls.sheet_names[-1]
        df_params = xls.parse(last_sheet)

        with pd.ExcelWriter(fichier_resultat, mode='a', engine='openpyxl') as writer:
            df_params.to_excel(writer, sheet_name='Paramètres machine', index=False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoAnalyzerUI()
    window.show()
    sys.exit(app.exec())