# 测试脚本
import cv2
import pytesseract

cap = cv2.VideoCapture(0)  # 或其他设备号
ret, frame = cap.read()
cv2.imwrite('test_frame11111111.png', frame)

# 测试OCR
text = pytesseract.image_to_string(frame, lang='chi_sim+eng')
print(text)