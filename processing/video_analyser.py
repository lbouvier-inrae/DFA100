#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: video_analyser.py
Author: Maxime Gosselin
Description: This script analyzes a video
Contact: maximeg391@gmail.com
License: MIT License
"""
import os
import cv2
from typing import List, Dict
from processing.image_analyser import analyse_image


def analyse_video(video_path: str, step: int = 1, scale: float = 1.0, agitation: int = 0) -> List[Dict[str, float]]:
    """
    Analyse une vidéo image par image à une fréquence donnée.

    Args:
        video_path (str): Chemin de la vidéo.
        fps_results (float): Nombre d'images à analyser par seconde.
        scale (float): Facteur d'échelle à appliquer sur les résultats.

    Returns:
        list: Liste de dictionnaires contenant les mesures pour chaque image.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Impossible d'ouvrir la vidéo : {video_path}")

    results = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx > agitation and frame_idx % step == 0:
            result = analyse_image(frame, scale=scale)
            print(result)
            result["frame"] = frame_idx
            results.append(result)

        frame_idx += 1

    cap.release()
    return results


if __name__ == "__main__":
    data = analyse_video("assets/test/video.avi")
    for entry in data:
        print(entry)