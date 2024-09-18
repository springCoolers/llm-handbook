"""
https://machinelearningknowledge.ai/easyocr-python-tutorial-with-examples/
"""

import easyocr
import cv2

# import cv2
print(cv2.__version__)

img = cv2.imread('sign_board.jpg')
# cv2.imshow(img)

reader = easyocr.Reader(['en'])

# 단어 단위로 출력
result = reader.readtext(img, detail = 0)
print(result)

# 문장 단위로 출력
result = reader.readtext(img, detail = 0, paragraph = True)
print(result)

# 각 단어별 detail(바운딩 박스 위치, 단어, 정확도) 출력
result = reader.readtext(img, detail = 1, paragraph = False)
print(result)

# 바운딩 박스를 그려줌
# for (coord, text, prob) in result:
#     (topleft, topright, bottomright, bottomleft) = coord
#     tx,ty = (int(topleft[0]), int(topleft[1]))
#     bx,by = (int(bottomright[0]), int(bottomright[1]))
#     cv2.rectangle(img, (tx,ty), (bx,by), (0, 0, 255), 2)
# cv2.imshow(img)


print('Good!')