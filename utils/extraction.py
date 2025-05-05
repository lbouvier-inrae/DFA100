import cv2
import os

def extract_frames(video_path, step=1):
    """
    Extrait des images d'une vidéo et les enregistre dans un dossier.

    Parameters:
        video_path (str): Chemin vers la vidéo.
        step (int): Nombre d’images à sauter entre deux extractions (1 = toutes les images).

    Returns:
        int: Nombre d'images extraites et sauvegardées.
    """
    os.makedirs("temp_frames", exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    saved_count = 0
    frame_index = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_index % step == 0:
            filename = f"temp_frames/frame_{saved_count:03d}.png"
            cv2.imwrite(filename, frame)
            saved_count += 1
        frame_index += 1
    
    cap.release()
    return saved_count