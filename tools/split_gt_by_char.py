import os
import cv2
from PIL import ImageFont
import subprocess

unit_dict = {}

def find_ttf_path():
    font_ttf_dict = {}
    result = subprocess.run(["fc-list", ":lang=ko"], stdout=subprocess.PIPE)  # fc-list 로 우분투 캐시에 등록된 폰트 목록 불러오기
    output = result.stdout.decode("utf-8")
    ttf_paths = [line.split(":")[0] for line in output.split("\n") if line]
    font_namess = [line.split(":")[1] for line in output.split("\n") if line]
    for i, font_names in enumerate(font_namess): 
        for font_name in font_names.split(','): 
            font_name = font_name.strip()
            new_font_name = ('_').join(font_name.split(' '))
            font_ttf_dict[new_font_name] = ttf_paths[i]
    return font_ttf_dict

def split_gt_by_char(gt_dir, model_name, extension, eval_list, font_ttf_dict):  
    eval_dir = f'../data/{model_name}-eval'
    cp_gt_dir = os.path.join(eval_dir, 'groundtruths')
    box_files = os.listdir(cp_gt_dir)
    wrong_results = []
    #####
    box_files = box_files[:10]
    ####
    for box_file in box_files: 
        box_file_name = os.path.splitext(box_file)[0]  #.exp0
        img_file = os.path.join(gt_dir, f'{box_file_name}.{extension}')
        font_name = ('.').join(('_').join(box_file_name.split('_')[:-2]).split('.')[1:])
        img = cv2.imread(img_file)
        #######
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        #######
        h, w, _ = img.shape
        try: 
            font = ImageFont.truetype(font_ttf_dict[font_name], 50)
        except: 
            wrong_results.append(box_file)
            continue
        page = int(box_file_name.split('_')[-1].split('-')[0])
        idx = int(box_file_name.split('-')[-1].split('.')[0])
        
        ## unit
        if font_name not in unit_dict.keys(): 
            j = 1
            while True: 
                tmp = 'kor.%s_page_0-%03d.exp0.tif'%(font_name, j)
                if os.path.exists(os.path.join(gt_dir, tmp)):
                    j += 1
                else:
                    unit_dict[font_name] = j - 1
                    break
        unit = unit_dict[font_name]
        
        gt = []
        gt_txt = '../data/langdata/kor/kor.training_text'
        with open(gt_txt, 'r') as f: 
            training_text = f.readlines()
            gt = training_text[unit*page+(idx-1)].strip()
        x_coor = 0
        with open(os.path.join(cp_gt_dir, box_file), 'w') as f: 
            for text in gt: 
                textwidth, textheight = font.getsize(text)
                x_coor += textwidth
            ratio = w / x_coor
            x_coor = 0
            for text in gt: 
                textwidth, textheight = font.getsize(text)
                f.write(f'{text} {int(x_coor*ratio)} 1 {int((x_coor+textwidth)*ratio)} {h-1} 0\n')
                ####
                #cv2.rectangle(img,(int(x_coor*ratio),1),(int((x_coor+textwidth)*ratio),h-1),(0,0,255),1)
                #####
                x_coor += textwidth
        ####
        #cv2.imwrite(f'result_{box_file_name}.png', img)
        ####
    print("wrong!! :", wrong_results)
    return(wrong_results)   
        
    
    '''
    #img_name = 'kor.GangwonEduHyeonokT_page_0-001.exp0'
    extension = 'tif'
    gt_txt = '../data/langdata/kor/kor.training_text'
    ####################
    box_file = f'{img_name}.box'
    img_file = f'{img_name}.{extension}'
    x_coor = 0
    img = cv2.imread(img_file)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, _ = img.shape
    #font = ImageFont.truetype("/usr/share/fonts/강원교육현옥샘.ttf", 50)
    #font = ImageFont.truetype("/usr/share/fonts/SANGJU Gyeongcheon Island.ttf", 50)
    font = ImageFont.truetype("/usr/share/fonts/영양군 음식디미방.ttf", 50)
    txt_name = os.path.splitext(img_name)[0]  # *.exp0.gt.txt
    page = int(txt_name.split('_')[-1].split('-')[0])
    idx = int(txt_name.split('-')[-1]) 
    # get unit
    temp = ('_').join(txt_name.split('_')[:-2])
    j = 1
    unit = 0
    while True: 
        tmp = '%s_page_0-%03d.exp0.tif'%(temp, j)
        if os.path.exists(os.path.join('../data/Hangul2-ground-truth', tmp)):
            j += 1
        else:
            unit = j - 1
            break
    # get gt txt from training_text use num and idx
    gt = []
    with open(gt_txt, 'r') as f: 
        #print(txt_name, unit*page+(idx-1))
        training_text = f.readlines()
        gt = training_text[unit*page+(idx-1)].strip()
        #f.write(gt)
    #############
    #gt_bbox_datas = []
    #with open(box_file, 'r') as f: 
        #gt_bbox_datas = f.readlines()
    with open(f'{img_name}.new.box', 'w') as f: 
        #for data in gt_bbox_datas: 
        for text in gt: 
            #text = data[0]
            textwidth, textheight = font.getsize(text)
            print(textheight)
            x_coor += textwidth
        ratio = w / x_coor
        x_coor = 0
        print(ratio)
        for text in gt: 
            textwidth, textheight = font.getsize(text)
            f.write(f'{text} {int(x_coor*ratio)} 1 {int((x_coor+textwidth)*ratio)} {h-1} 0\n')
            cv2.rectangle(img,(int(x_coor*ratio),1),(int((x_coor+textwidth)*ratio),h-1),(0,0,255),1)
            x_coor += textwidth
    cv2.imwrite(f'result_{img_name}.png', img)            '''
        
    
import shutil
    
if __name__ == '__main__': 
    gt_dir = '../data/Hangul2-ground-truth'
    eval_list = os.path.join('../data/', "Hangul2", 'list.eval')
    eval_dir = os.path.join('../data/Hangul2-eval')
    
    with open(eval_list, 'r') as f: 
        a = 0
        while True: 
            line = f.readline()
            if line and a < 10: 
                img_name = os.path.splitext(line.split(os.sep)[-1])[0]
                shutil.copy(os.path.join(gt_dir, f'{img_name}.box'),
                            os.path.join(eval_dir, 'groundtruths', f'{img_name}.box'))
                a += 1
            else: break
    print("move files done!")
    
    font_ttf_dict = find_ttf_path()
    split_gt_by_char(gt_dir, 'Hangul2', 'tif', eval_list, font_ttf_dict)
    
    '''
    size = 60
    font = ImageFont.truetype("/usr/share/fonts/SANGJU Gyeongcheon Island.ttf", size)
    textx = ["제", "조", "사", "내", "용"]
    for text in textx: 
        width, height = font.getsize(text)
        print(width, height)
    '''