import os
import shutil

gt_root = '/opt/level3_productserving-level3-cv-11/model/tesstrain/data/Hangul2-ground-truth'
imgs_root = '/opt/level3_productserving-level3-cv-11/model/tesstrain/data/Hangul2-ground-truth-tmp'

fonts = set()
tmp_fonts = os.listdir(imgs_root)
for font in tmp_fonts: 
    if font == 'kor': 
        continue
    fonts.add(font.split('.')[1])  # ex) kor.KoreanPOBBOR.exp0.tif
print(len(fonts), "fonts :", fonts)

lang = 'kor'
for font in fonts: 
    i = 0
    while True:
        image_name = '%s.%s_page_%d.tif'%(lang, font, i)
        try: 
            shutil.move(os.path.join(gt_root, image_name), imgs_root)
            i += 1
        except: 
            break
        
        
#'%s/%s_page_%s.tif'%(gt_root, name, i)

#kor.HanS_page_15        