import cv2
import numpy as np
from processing.image_analyser import analyse_image

def analyse_video(path_to_video, fps_results=1):
    cap = cv2.VideoCapture(path_to_video)
    
    fps_video = cap.get(cv2.CAP_PROP_FPS)
    if (fps_results > fps_video):
        fps_results = fps_video
    
    frame_step = 1 / (fps_video * fps_results)
    frame_step = round(frame_step)
    
    if not cap.isOpened():
        print("Erreur : impossible d'ouvrir la vidéo.")
        return
    
    results = []
    
    frame_index = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_index % frame_step == 0:
            results.append(analyse_image(frame))
            results[-1]["frame"] = frame_index + 1
            results[-1]["number"] = len(results)
        
        frame_index += 1
    cap.release()
    return results

if __name__=="__main__":
    print(analyse_video("assets/test/video01.avi", 1))