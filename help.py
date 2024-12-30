import cv2
import numpy as np

def draw_circles(storage, output):
    circles = np.asarray(storage)
    for circle in circles[0, :]:
        Radius, x, y = int(circle[2]), int(circle[0]), int(circle[1])
        cv2.circle(output, (x, y), 1, (0, 255, 0), -1, 8, 0)
        cv2.circle(output, (x, y), Radius, (255, 0, 0), 3, 8, 0)    

# Use raw string for the file path to avoid issues with backslashes
orig_path = r'C:\Users\Lenovo\Downloads\Iris Recognition\images\eyes\S1001R02.jpg'
orig = cv2.imread(orig_path)
if orig is None:
    raise FileNotFoundError(f"The original image could not be loaded from {orig_path}. Check the file path.")

processed = cv2.imread(orig_path, cv2.IMREAD_GRAYSCALE)
if processed is None:
    raise FileNotFoundError(f"The grayscale image could not be loaded from {orig_path}. Check the file path.")

# Use Canny, as HoughCircles seems to prefer ring-like circles to filled ones.
processed = cv2.Canny(processed, 5, 70, 3)
# Smooth to reduce noise a bit more
processed = cv2.GaussianBlur(processed, (7, 7), 1.5)

circles = cv2.HoughCircles(processed, cv2.HOUGH_GRADIENT, 2, 100, param1=30, param2=150, minRadius=60, maxRadius=300)

if circles is not None:
    draw_circles(circles, orig)
else:
    print("No circles were found.")

cv2.imshow("Original with Circles", orig)
cv2.waitKey(0)
cv2.destroyAllWindows()

