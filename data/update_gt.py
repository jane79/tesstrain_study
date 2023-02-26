import os
from tqdm import tqdm
import logging
import shutil

is_anything_wrong = False

fonts = set()
wrong_fonts = set()
tmp_root = './Hangul2-ground-truth-tmp'
tmp_fonts = os.listdir(tmp_root)
for font in tmp_fonts: 
    if font == 'kor': 
        continue
    if font.split('.')[-1] == 'tif' and font.split('.')[-2] != 'exp0': 
        tmp = font.split('.')[1].split('_')[:-2]
        fonts.add(('_').join(tmp))  # ex) kor.KoreanPOBBOR.exp0.tif
print(len(fonts), "fonts :", fonts)

training_text_f = open("./langdata/kor/kor.training_text", 'r')
training_text = training_text_f.readlines()
training_text_f.close()
print("training_text :", len(training_text))

lang = 'kor'
gt_root = './Hangul2-ground-truth'
unit_dict = {}
for font in fonts: 
    j = 1  # idx
    # get lines number(unit) per page for each font
    while True:  # 0페이지 줄 개수
        tmp = '%s.%s_page_0-%03d.exp0.tif'%(lang, font, j)
        if os.path.exists(os.path.join(gt_root, tmp)): 
            j += 1
        else: 
            unit_dict[font] = j - 1
            break
    # 제대로(다) 안 나눠진 파일 있는지 확인
    cnt = 0  # 이미지 개수
    i, j = 0, 1  # page, idx
    while True: 
        # 이미지 개수가 training_text 줄 개수와 같은가
        tmp = '%s.%s_page_%d-001.exp0.tif'%(lang, font, i)
        if os.path.exists(os.path.join(gt_root, tmp)): 
            j = 1
            while True: 
                tmp = '%s.%s_page_%d-%03d.exp0.tif'%(lang, font, i, j)
                if os.path.exists(os.path.join(gt_root, tmp)): 
                    j += 1
                    cnt += 1
                else: 
                    break
            i += 1
        else: 
            if cnt != len(training_text):  # 이미지 개수가 training_text가 다르다면
                print(f'{font}의 분할 이미지 개수가 다릅니다 : {cnt}')
                unit_dict.pop(font, None)
                wrong_fonts.add(font)
                is_anything_wrong = True
            cnt = 0
            break
    if font in unit_dict: 
        unit_cnt = (i-1) * unit_dict[font] + (j-2)
        if unit_cnt != len(training_text)-1: 
            print(f'{font}의 페이지별 줄 개수가 일정하지 않습니다 : {unit_cnt}')
            unit_dict.pop(font, None)
            wrong_fonts.add(font)
            is_anything_wrong = True
        
        
cnt = 0 
print("UNITS")
for key, val in unit_dict.items(): 
    print(key, val, end=' | ')
    cnt += val
print("========================================")

if is_anything_wrong: 
    print(wrong_fonts)
    while True:
        ans = input("문제가 있는 파일들이 있습니다. 해당 파일들을 제외하고 update를 진행하시겠습니까? (y/n)")
        if ans == 'n': 
            exit()
        elif ans != 'y': 
            print("잘못된 키 입력")
        else: 
            break
# update *.gt.txt
# 잘못된 키 제거
while wrong_fonts: 
    font = wrong_fonts.pop()
    i = 0
    while True: 
        tmp = '%s.%s_page_%d-001.exp0.gt.txt'%(lang, font, i)
        if os.path.exists(os.path.join(gt_root, tmp)): 
            j = 1
            while True: 
                tmp_tif = '%s.%s_page_%d-%03d.exp0.tif'%(lang, font, i, j)
                tmp_txt = '%s.%s_page_%d-%03d.exp0.gt.txt'%(lang, font, i, j)
                if os.path.exists(os.path.join(gt_root, tmp_txt)): 
                    shutil.move(os.path.join(gt_root, tmp_tif), 'Hangul2-ground-truth-wrong/')
                    shutil.move(os.path.join(gt_root, tmp_txt), 'Hangul2-ground-truth-wrong/')
                    j += 1
                    cnt += 1
                else: 
                    break
            i += 1
        else: 
            break

txts = os.listdir(gt_root)
#print(txts, len(txts))
for txt in tqdm(txts): 
    if txt.split('.')[-1] == "txt": 
        # get page num and idx
        txt_name = ".".join(txt.split('.')[:-3])  # *.exp0.gt.txt
        page = int(txt_name.split('_')[-1].split('-')[0])
        idx = int(txt_name.split('-')[-1])
        font = txt_name.split('.')[1].split('_')[:-2]
        font = "_".join(font)
        unit = unit_dict[font]
        # get gt txt from training_text use num and idx
        with open(os.path.join(gt_root, txt), 'w') as f: 
            #print(txt_name, unit*page+(idx-1))
            gt = training_text[unit*page+(idx-1)].strip()
            f.write(gt)

        # kor.KoreanPOBBOR_page_4-034.exp0.txt
