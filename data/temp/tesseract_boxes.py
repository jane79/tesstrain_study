import pytesseract
import cv2 
import matplotlib.pyplot as plt
from PIL import Image
import os



'''
paths = ['가_89300.png',
         '뀜_84868.png',
         '낡_84897.png',
         'test_3.png']  # 인풋 이미지 경로
result_root = './result/'  # box 그려진 이미지 저장 경로
#tessdata_dir_config = r'--tessdata-dir "/opt/level3_productserving-level3-cv-11/model/tesstrain/data/Hangul2"'
# Hangul_8.369000_16772_17200

for path in paths: 
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    custom_oem_psm_config = r'--oem 1 --psm 6'

    # use Tesseract to OCR the image 
    name = path.split('/')[-1]
    print(name)
    hImg,wImg,_ = img.shape
    boxes = pytesseract.image_to_boxes(img, lang='kor', config=custom_oem_psm_config)
    for b in boxes.splitlines(): 
        b = b.split(' ')
        x,y,w,h = int(b[1]),int(b[2]),int(b[3]),int(b[4])
        cv2.rectangle(img,(x,hImg-y),(w,hImg-h),(0,0,255),1)
        cv2.putText(img,b[0],(x,hImg-y+20),cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,255),1)
    text = pytesseract.image_to_string(img, lang='kor', config=custom_oem_psm_config)
    if not os.path.exists(result_root): 
        os.mkdir(result_root)
    cv2.imwrite(os.path.join(result_root, name), img)
    print(text)'''


#hocr test
from bs4 import BeautifulSoup
import subprocess

command = "tesseract test_6.png stdout --oem 1 -l kor_han2 --psm 6 -c hocr_char_boxes=1 hocr"
result = subprocess.run(command.split(' '), stdout=subprocess.PIPE)
hocr_output = result.stdout.decode("utf-8")
soup = BeautifulSoup(hocr_output, "lxml")
cinfos = soup.find_all('span', {"class":"ocrx_cinfo"})
for cinfo in cinfos: 
    print(f"{cinfo.text}")
    print(f"{cinfo['title']}")


'''path = 'test_6.png'
img = cv2.imread(path)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
custom_oem_psm_config = r'--oem 1 --psm 6'
hocr = pytesseract.image_to_pdf_or_hocr('test_6.png',
                                        extension='hocr',
                                        lang='kor_han2',
                                        config=custom_oem_psm_config)
hocr_str = hocr.decode()
soup = BeautifulSoup(hocr, "lxml")'''

#page= soup.find_all('span', {"class":"ocrx_word"})
#print(page)
#page= soup.find('body', {"class":"ocr_page"})
#print(soup)
    
'''import pytesseract
import cv2

path = 'test_6.png'
img = cv2.imread(path)
image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

boxes = [[18, 17, 110, 77],
         [11, 27, 177, 138],
         [193, 16, 298, 142],
         [318, 62, 357, 117],
         [364, 45, 416, 121]]

for x1, y1, x2, y2 in boxes:
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 1)
    cv2.imwrite(f'result_han2_{path}', image)
 '''