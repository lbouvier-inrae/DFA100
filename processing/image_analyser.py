# processing/image_analyser.py

import cv2
import numpy as np
from skimage.filters import threshold_otsu
from typing import Dict


def convert_to_grayscale(frame: np.ndarray) -> np.ndarray:
    """Convertit une image couleur en niveau de gris."""
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def binarize_image(gray_frame: np.ndarray, threshold: float) -> np.ndarray:
    """Binarise une image en niveau de gris avec un seuil donné."""
    _, binary = cv2.threshold(gray_frame, threshold, 255, cv2.THRESH_BINARY)
    return binary


def extract_contour_areas(binary_image: np.ndarray) -> list:
    """Extrait les aires des contours détectés dans une image binaire."""
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [cv2.contourArea(c) for c in contours]


def analyse_image(frame: np.ndarray, scale: float = 1.0) -> Dict[str, float]:
    """
    Analyse une image pour détecter les bulles et retourner des statistiques.
    
    Args:
        frame (np.ndarray): Image en couleur (BGR).
        scale (float): Rapport de conversion pixels -> unité réelle (optionnel).

    Returns:
        dict: Dictionnaire contenant nb de bulles, surface moyenne et écart type.
    """
    gray = convert_to_grayscale(frame)
    threshold = threshold_otsu(gray)
    
    # Pour le développement, seuil fixe (temporaire)
    threshold = 2  
    
    binary = binarize_image(gray, threshold)
    areas = extract_contour_areas(binary)

    nb_bulles = len(areas)
    moyenne = np.mean(areas) if areas else 0.0
    ecart_type = np.std(areas) if areas else 0.0

    return {
        "nb_bulles": nb_bulles,
        "surface_moyenne[px]": moyenne,
        "ecart_type[px]": ecart_type
    }


if __name__ == "__main__":
    image = cv2.imread("assets/results/frame/image_0005.png")
    result = analyse_image(image)
    result["frame"] = 1
    print(result)
