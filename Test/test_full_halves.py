import cv2

path = r'e:\Tool\QuestionROK\debug_ocr\full.png'
img = cv2.imread(path)
h, w = img.shape[:2]

left_half = img[:, :w//2]
right_half = img[:, w//2:]

print("Left half mean:", left_half.mean())
print("Right half mean:", right_half.mean())

cv2.imwrite(r'e:\Tool\QuestionROK\debug_ocr\left_half.png', left_half)
cv2.imwrite(r'e:\Tool\QuestionROK\debug_ocr\right_half.png', right_half)

import os
print("left_half.png size:", os.path.getsize(r'e:\Tool\QuestionROK\debug_ocr\left_half.png'))
print("right_half.png size:", os.path.getsize(r'e:\Tool\QuestionROK\debug_ocr\right_half.png'))
