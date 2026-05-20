import cv2

for opt in ['opt_a.png', 'opt_b.png', 'opt_c.png', 'opt_d.png', 'full.png', 'question.png']:
    path = f'e:\\Tool\\QuestionROK\\debug_ocr\\{opt}'
    img = cv2.imread(path)
    if img is not None:
        print(f"{opt}: shape={img.shape}")
    else:
        print(f"{opt}: failed to load")
