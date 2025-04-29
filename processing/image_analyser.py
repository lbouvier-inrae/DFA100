import cv2
import numpy as np
from skimage.filters import threshold_otsu

def analyse_image(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    threshold = threshold_otsu(gray_frame)
    
    _, thresh = cv2.threshold(gray_frame, threshold, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    areas = [cv2.contourArea(c) for c in contours]
    
    nb_bulles = len(areas)
    moyenne = np.average(areas).item()
    ecart_type = np.std(areas).item()
    
    return {
        "nb_bulles": nb_bulles,
        "moyenne": moyenne,
        "ecart_type": ecart_type
        }
    
    


if __name__=="__main__":
    image = cv2.imread("assets/test/im_1.png")
    result = analyse_image(image)
    result["frame"] = 1
    print(result)