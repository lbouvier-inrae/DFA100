import sys
import os
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QFileDialog, QSlider, QHBoxLayout,
    QLineEdit, QDateEdit
)
import pandas as pd
from PySide6.QtCore import (Qt, QDate)
from processing.video_analyser import analyse_video

class VideoAnalyzerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analyseur de vidéo de bulles")
        self.setMinimumSize(600, 400)

        self.init_ui()

    def init_ui(self):
        self.machine_excel_path = False
        
        layout = QVBoxLayout()
        
        # Bouton pour charger une video
        self.load_button = QPushButton("Charger une vidéo")
        self.load_button.clicked.connect(self.load_video)
        layout.addWidget(self.load_button)
        
        # Label et Input pour le nom de l'expérience
        self.name_experience_label = QLabel("Nom de l'expérience :")
        self.name_experience_input = QLineEdit("")
        self.name_experience_input.setPlaceholderText("lait")
        self.name_experience_input.textChanged.connect(self.update_result_filename)
        
        name_experience_box = QHBoxLayout()
        name_experience_box.addWidget(self.name_experience_label)
        name_experience_box.addWidget(self.name_experience_input)
        
        layout.addLayout(name_experience_box)

        # Selecteur de la date
        self.date_label = QLabel("Date de l'expérience :")
        self.date_selector = QDateEdit(QDate.currentDate())
        self.date_selector.dateChanged.connect(self.update_result_filename)
        
        date_box = QHBoxLayout()
        date_box.addWidget(self.date_label)
        date_box.addWidget(self.date_selector)
        
        layout.addLayout(date_box)
        
        # Sélecteur de fichier Excel machine
        self.excel_button = QPushButton("Charger les paramètres machine (Excel)")
        self.excel_button.clicked.connect(self.load_excel)
        layout.addWidget(self.excel_button)

        self.excel_path = None  # Pour stocker le chemin

        
        # Slider pour le nombre d'images par seconde analysées
        slider_layout = QHBoxLayout()
        self.fps_slider = QSlider(Qt.Horizontal)
        self.fps_slider.setMinimum(1)
        self.fps_slider.setMaximum(20)
        self.fps_slider.setValue(10)
        self.fps_slider.setTickInterval(1)
        self.fps_slider.setTickPosition(QSlider.TicksBelow)

        self.slider_label = QLabel("Images analysées par seconde : 1")
        self.fps_slider.valueChanged.connect(
            lambda val: self.slider_label.setText(f"Images analysées par seconde : {val/10}")
        )

        slider_layout.addWidget(self.slider_label)
        slider_layout.addWidget(self.fps_slider)
        layout.addLayout(slider_layout)
        
        
        # Label et Input pour le nom du fichier resultat
        self.name_result_label = QLabel("Nom du fichier de résultat :")
        self.name_result_input = QLineEdit("")
        self.name_result_input.setPlaceholderText("resultat.xlsx")
        
        name_result_box = QHBoxLayout()
        name_result_box.addWidget(self.name_result_label)
        name_result_box.addWidget(self.name_result_input)
        
        layout.addLayout(name_result_box)

        # Bouton de lancement de l'analyse
        self.analyze_button = QPushButton("Lancer l’analyse")
        self.analyze_button.clicked.connect(self.analyze_video)
        layout.addWidget(self.analyze_button)
        
        self.status_label = QLabel("Prêt")
        layout.addWidget(self.status_label)


        self.setLayout(layout)

    def load_video(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Choisir une vidéo", "", "Videos (*.avi *.mp4)")
        if self.file_path:
            stat = os.stat(self.file_path)
            self.date_selector.setDate(datetime.fromtimestamp(stat.st_birthtime))
            self.name_experience_input.setText(Path(self.file_path).stem)
            self.update_result_filename

    def analyze_video(self):
        self.status_label.setText("Analyse en cours...")
        QApplication.processEvents()
        
        results = analyse_video(self.file_path, self.fps_slider.value()/10)
        df = pd.DataFrame(results)
        
        result_path = f"assets/results/{self.name_result_input.text()}"
        
        df.to_excel(result_path, index=False)
        if self.machine_excel_path:
            self.ajouter_parametres_machine(result_path, self.machine_excel_path)
        
        self.status_label.setText("Analyse terminée")

    def update_result_filename(self):
        date_str = self.date_selector.date().toString("yyyy_MM_dd")
        name = self.name_experience_input.text().strip() or "experience"
        self.name_result_input.setText(f"{name}_{date_str}.xlsx")
        
    def load_excel(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir un fichier Excel", "", "Excel Files (*.xlsx *.xls)")
        if path:
            self.machine_excel_path = path

    def ajouter_parametres_machine(self, fichier_resultat, fichier_excel):
        if not fichier_excel:
            return
        
        # Lire toutes les feuilles
        xls = pd.ExcelFile(fichier_excel)
        last_sheet = xls.sheet_names[-1]
        df_params = xls.parse(last_sheet)

        # Ajouter la feuille à ton fichier résultat
        with pd.ExcelWriter(fichier_resultat, mode='a', engine='openpyxl') as writer:
            df_params.to_excel(writer, sheet_name='Paramètres machine', index=False)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoAnalyzerUI()
    window.show()
    sys.exit(app.exec())
