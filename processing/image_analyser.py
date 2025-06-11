#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: image_analyser.py
Author: Maxime Gosselin
Description: This script analyzes an image to provide a dictionary of results
Contact: maximeg391@gmail.com
License: MIT License
"""
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
    
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    areas_px = [cv2.contourArea(c) for c in contours]
    areas_px.pop(0)
    
    scale_factor = (1 / (scale ** 2)) if scale > 0 else 1
    areas_cm = [a * scale_factor for a in areas_px]

    nb_bulles = len(areas_cm)
    moyenne = float(np.average(areas_cm)) if areas_cm else 0.0
    ecart_type = float(np.std(areas_cm)) if areas_cm else 0.0

    return {
        "nb_bulles": nb_bulles,
        "surface_moyenne[mm²]": moyenne,
        "ecart_type[mm²]": ecart_type
    }
