import numpy as np
import cv2


def skew_angle(image: np.ndarray, DEBUG: bool = False) -> float:
    """
    Function to detect the edges (lines) in an image
    and calculate the skew angle. Ideally, the lines
    should be drawn parallel to text direction
    or obvious image borders.

    If DEBUG=TRUE, show image with lines drawn
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 200, 200)

    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi / 180,
                            threshold=80, minLineLength=120,
                            maxLineGap=10)
    deg_angles = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]

            # hough lines returns a list of lines with points
            # in the form (x1, y1, x2, y2).
            # The first step is to calculate the slopes of
            # these lines from their paired point values
            slope = (y2 - y1) / (x2 - x1)

            # it just so happens that this slope is also
            # y where y = tan(theta), the angle
            # in a circle by which the line is offset
            rad_angle = np.arctan(slope)
            deg_angles.append(np.degrees(rad_angle))

        if DEBUG:
            copy = image.copy()
            for line in lines:
                x1, y1, x2, y2 = line[0]

                slope = (y2 - y1) / (x2 - x1) if (x2 - x1) else 0
                rad_angle = np.arctan(slope)
                deg_angle = np.degrees(rad_angle)

                cv2.line(copy, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(copy, str(np.round(deg_angle)), (x1, y1),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1)
            cv2.imshow('image', copy)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # which of these degree values is most common?
        hist = np.histogram(deg_angles, bins=180)
        angle = hist[1][np.argmax(hist[0])]

        return angle

    return 0.0


def rotate(image: np.ndarray, degrees: float) -> np.ndarray:
    """
    Function to rotate an image counter-clockwise
    by X degrees, where X is in the range [-360, 360]
    """

    (oldX, oldY) = image.shape[1], image.shape[0]
    mat = cv2.getRotationMatrix2D(center=(oldX / 2, oldY / 2),
                                angle=degrees,
                                scale=1.0)  # rotate about center of image.

    # include this if you want to prevent corners being cut off
    r = np.deg2rad(degrees)

    newX, newY = (abs(np.sin(r) * oldY) + abs(np.cos(r) * oldX),
                  abs(np.sin(r) * oldX) + abs(np.cos(r) * oldY))

    # warpAffine function call, below, basically works like this:
    # 1. apply the M transformation on each pixel of the original image
    # 2. save everything that falls within the upper-left "dsize"
    #    portion of the resulting image.

    # find the translation that moves the result to the center of that region.
    (tx, ty) = ((newX - oldX) / 2, (newY - oldY) / 2)

    # third column of matrix holds translation,
    # which takes effect after rotation.
    mat[0, 2] += tx
    mat[1, 2] += ty

    rotated = cv2.warpAffine(image, mat, dsize=(int(newX), int(newY)))
    return rotated
