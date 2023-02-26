import os
import pytesseract
from metric import *
from glob import glob
import json
import shutil
import cv2
#import split_gt_by_char.split_gt_by_char
from split_gt_by_char import *

data_root = '../data/'
model_name = 'Hangul2'
eval_dir = os.path.join(data_root, f'{model_name}-eval')  # gt and inf .box & .gt 포함
gt_dir = os.path.join(data_root, f'{model_name}-ground-truth')

extension, lang = 'tif', 'kor_han2'  # Hangul2
if model_name == 'Letter2': 
    extension, lang = 'png', 'kor_letter2'
elif model_name == 'Letter':  # augmentation tuning, 나중에 할 것.
    extension, lang = 'png', 'kor_letter'
elif model_name == 'Hangul': 
    extension, lang = 'tif', 'kor_han'

classes = []
with open('ko.json', 'r') as f: 
    json_data = json.load(f)
    classes = json_data["words"]["character"]
classes = sorted(classes)

eval_list = os.path.join(data_root, model_name, 'list.eval')

# gt는 여기서, detection은 bounding box에서 파일 생성!
with open(os.path.join(data_root, model_name, 'list.eval'), 'r') as f: 
    while True: 
        line = f.readline()
        if line: 
            img_name = os.path.splitext(line.split(os.sep)[-1])[0]
            shutil.copy(os.path.join(gt_dir, f'{img_name}.box'),
                        os.path.join(eval_dir, 'groundtruths', f'{img_name}.box'))
        else: break
print("move files done!")

if model_name == 'Hangul' or model_name == 'Hangul2': 
    font_ttf_dict = find_ttf_path()
    wrong_results = split_gt_by_char(gt_dir, model_name, extension, eval_list, font_ttf_dict)
    for wrong_box_file in wrong_results:
        os.remove(os.path.join(eval_dir, 'groundtruths', wrong_box_file))

detections, gts = boundingBoxes(eval_dir, gt_dir , extension, classes, eval_list, lang)
## for backup
with open(os.path.join(f'backup_dir_{model_name}', 'detections.txt', ), 'w') as f: 
    for detection in detections: 
        img_name, label, conf, bbox = detection
        lx, bot, rx, top = bbox
        f.write(f'{img_name} {label} {conf} {lx} {bot} {rx} {top}\n')
with open(os.path.join(f'backup_dir_{model_name}', 'gts.txt', ), 'w') as f: 
    for gt in gts: 
        img_name, label, conf, bbox = gt
        lx, bot, rx, top = bbox
        f.write(f'{img_name} {label} {conf} {lx} {bot} {rx} {top}\n')
## for backup

## if restart from AP
'''
detections, gts = [], []
with open(os.path.join('backup_dir', 'detections.txt', ), 'r') as f: 
    lines = f.readlines()
    for line in lines: 
        img_name, label, conf, lx, bot, rx, top = line.strip().split()
        conf = float(conf)
        lx, bot, rx, top = map(int, [lx, bot, rx, top])
        boxinfo = [img_name, label, conf, (lx, bot, rx, top)]
        detections.append(boxinfo)
        
with open(os.path.join('backup_dir', 'gts.txt', ), 'r') as f: 
    lines = f.readlines()
    for line in lines: 
        img_name, label, conf, lx, bot, rx, top = line.strip().split()
        conf = float(conf)
        lx, bot, rx, top = map(int, [lx, bot, rx, top])
        boxinfo = [img_name, label, conf, (lx, bot, rx, top)]
        gts.append(boxinfo)
'''

#AP(detections, gts, classes)
result_ap = AP(detections, gts, classes)
result_map = mAP(result_ap)
print(f"result_map is {result_map}!!!")
