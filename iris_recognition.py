import numpy as np
import os
import cv2

centroid = (0, 0)

radius = 0

currentEye = 0

eyesList = []

def getNewEye(list):
    global currentEye
    if currentEye >= len(list):
        currentEye = 0
    newEye = list[currentEye]
    currentEye += 1
    return newEye

def getIris(frame):
    copyImg = frame.copy()
    resImg = frame.copy()
    grayImg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mask = np.zeros_like(grayImg)
    edges = cv2.Canny(grayImg, 5, 70, 3)
    cv2.GaussianBlur(edges, (7, 7), 2)
    circles = getCircles(grayImg, edges)
    if circles is not None:
        for circle in circles[0, :]:
            rad = int(circle[2])
            global radius
            radius = rad
            cv2.circle(mask, centroid, rad, 255, thickness=-1)
            resImg = cv2.bitwise_and(resImg, resImg, mask=mask)
            x = int(centroid[0] - rad)
            y = int(centroid[1] - rad)
            w = int(rad * 2)
            h = w
            cropImg = resImg[y:y + h, x:x + w]
            return cropImg, edges, circles
    return resImg, edges, None

def getCircles(image, edges):
    for i in range(80, 151):
        circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, dp=2, minDist=100, param1=30, param2=i, minRadius=100,
                                   maxRadius=140)
        if circles is not None and len(circles[0]) == 1:
            # Draw the circle on the edges image
            for circle in circles[0, :]:
                center = (int(circle[0]), int(circle[1]))
                radius = int(circle[2])
                cv2.circle(edges, center, radius, (255, 255, 255), 2)
            return circles
    return None

def getPupil(frame):
    pupilImg = cv2.inRange(frame, (30, 30, 30), (80, 80, 80))
    contours, _ = cv2.findContours(pupilImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 50:
            M = cv2.moments(contour)
            x = int(M["m10"] / M["m00"])
            y = int(M["m01"] / M["m00"])
            global centroid
            centroid = (x, y)
            cv2.drawContours(frame, [contour], -1, (0, 0, 0), thickness=cv2.FILLED)
            break
    return frame

def getPolar2CartImg(image, rad):
    imgSize = image.shape[:2]
    c = (imgSize[1] / 2, imgSize[0] / 2)
    imgRes = cv2.warpPolar(image, (360, rad * 3), c, 60.0, cv2.INTER_LINEAR + cv2.WARP_FILL_OUTLIERS)
    imgRes = cv2.rotate(imgRes, cv2.ROTATE_90_CLOCKWISE)
    return imgRes

cv2.namedWindow("input", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("output", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("normalized image", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("iris", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("pupil", cv2.WINDOW_AUTOSIZE)

eyesList = os.listdir('images/eyes')
key = 0
while True:
    eye = getNewEye(eyesList)
    frame = cv2.imread("images/eyes/" + eye)
    
    if frame is None:
        print(f"Failed to load image: images/eyes/{eye}")
        continue
    
    iris = frame.copy()
    output = getPupil(frame)
    iris, edges, circles = getIris(output)
    
    if iris is None or iris.size == 0:
        print(f"Failed to process iris for image: images/eyes/{eye}")
        continue
    
    cv2.imshow("input", frame)
    cv2.imshow("output", iris)
    cv2.imshow("iris", edges)
    
    if circles is not None:
        circle_fit_img = frame.copy()
        for circle in circles[0, :]:
            center = (int(circle[0]), int(circle[1]))
            radius = int(circle[2])
            cv2.circle(circle_fit_img, center, radius, (0, 255, 0), 2)
        cv2.imshow("pupil", circle_fit_img)
    
    normImg = getPolar2CartImg(iris, radius)
    
    if normImg is None or normImg.size == 0:
        print(f"Failed to normalize iris for image: images/eyes/{eye}")
        continue
    
    cv2.imshow("normalized image", normImg)
    
    key = cv2.waitKey(3000)
    # Exit on ESC key
    if key == 27:
        break

cv2.destroyAllWindows()
