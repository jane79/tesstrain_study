import os
from metric import *
from tqdm import tqdm

def n_divide_boundingBoxes(labelPath, imagePath, extension, classes): 
    detections, groundtruths, eval_list = [], [], []
    eval_list = os.listdir(imagePath)
    for line in tqdm(eval_list): 
        line = line.strip()
        img_name = os.path.splitext(line)[0]
        
        if os.path.exists(os.path.join(labelPath, 'groundtruths', f'{img_name}.box')): 
            for boxtype in ['detection', 'groundtruths']:
                boxtypeDir = os.path.join(labelPath,boxtype)
                
                if boxtype == 'detection': 
                    img = cv2.imread(os.path.join(imagePath, line))
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    h, w, _ = img.shape
                    x1, y1, x2, y2 = 0, 0, w, h
                    txt = ''
                    with open(os.path.join(labelPath, f'groundtruths/{img_name}.box'), 'r') as f: 
                        txt = f.readlines()[0].strip()
                    char_width = np.array([0.])
                    char_true = []
                    for order, tx in enumerate(txt):
                        flag = 0
                        if order == len(txt) -1 or order == 0:
                            flag = 1.5
                        if tx.isalpha():
                            char_width = np.append(char_width,10 + flag)
                            char_true.append(True)
                        elif tx in "?~^":
                            char_width = np.append(char_width,6 + flag)
                            char_true.append(False)
                        elif tx in "!., ":
                            char_width = np.append(char_width,3.3 + flag)
                            char_true.append(False)
                    char_width *= (x2-x1) / np.sum(char_width)
                    char_width = np.round(char_width, 0)
                    char_width = np.cumsum(char_width)
                    char_width = char_width.tolist()
                    
                    img_crop_letters = []
                    for i in range(len(char_width)-1):
                        if char_true[i]:  # 좌상단 : (x1+int(char_width[i], y1) 우하단 : (x1 + int(char_width[i+1]), y2))
                            #img_crop_letter = img[y1 : y2+1, x1 + int(char_width[i]) : x1 + int(char_width[i+1])] # img croped
                            boxinfo = [img_name, txt[i], 1,
                                       (x1+int(char_width[i]), y1,
                                        x1+int(char_width[i+1]), y2)]
                            detections.append(boxinfo)
                    
                            cv2.rectangle(img, (x1+int(char_width[i]), y1), (x1+int(char_width[i+1]), y2), (0,0,255), 1)
                    cv2.imwrite(f'untypical_result/result_{line}', img)
                    #print(detections)      
                                          
                else:  # groundtruths
                    labelinfos = []
                    with open(os.path.join(boxtypeDir, f'{img_name}.box'), 'r') as f_gt:
                        labelinfos = f_gt.readlines()    
                    for labelinfo in labelinfos[1:]: 
                        try: 
                            label, lx, bot, rx, top, _ = map(str, labelinfo.strip().split())
                            if label not in classes:
                                continue
                            lx, bot, rx, top = map(int, [lx, bot, rx, top])
                            conf = 1.0
                            boxinfo = [img_name, label, conf, (lx, bot, rx, top)]
                            groundtruths.append(boxinfo)
                        except: continue
                        
    return detections, groundtruths



def boundingBoxesUn(labelPath, imagePath, extension, classes, evalList, lang):   # Letter2-eval  
    detections, groundtruths, eval_list = [], [], []
    with open(evalList, 'r') as f: 
        eval_list = f.readlines()
    
    for line in tqdm(eval_list): 
        line = line.strip()
        img_name = os.path.splitext(line.split(os.sep)[-1])[0]
        if os.path.exists(os.path.join(labelPath, 'groundtruths', f'{img_name}.box')): 
            for boxtype in ['detection', 'groundtruths']:
                boxtypeDir = os.path.join(labelPath,boxtype)
                if boxtype == 'detection': 
                    img = os.path.join(imagePath, f'{img_name}.{extension}')
                    command = f"tesseract {img} stdout --oem 1 -l {lang} --psm 6 -c hocr_char_boxes=1 hocr"
                    result = subprocess.run(command.split(' '), stdout=subprocess.PIPE)
                    hocr_output = result.stdout.decode("utf-8")
                    soup = BeautifulSoup(hocr_output, "lxml")
                    cinfos = soup.find_all('span', {"class":"ocrx_cinfo"})    
                    temp_detections = []
                    with open(os.path.join(boxtypeDir, f'{img_name}.box'), 'w') as f_dt: 
                        for cinfo in cinfos: 
                            label = cinfo.text
                            bbox, x_conf = cinfo['title'].split(';')
                            lx, bot, rx, top = map(int, bbox.strip().split()[1:])
                            f_dt.write(f'{label} {lx} {bot} {rx} {top}\n')
                            conf = float(x_conf.strip().split()[-1])
                            boxinfo = [img_name, label, conf, (lx, bot, rx, top)]
                            detections.append(boxinfo)
                            temp_detections.append(boxinfo)
                    ##########
                    imgcv = cv2.imread(os.path.join(imagePath, f'{img_name}.{extension}'))
                    for temp_detection in temp_detections: 
                        imgcv = cv2.cvtColor(imgcv, cv2.COLOR_BGR2RGB)
                        lx, bot, rx, top = temp_detection[-1]
                        cv2.rectangle(imgcv, (lx, bot), (rx, top), (0,0,255), 1)
                    cv2.imwrite(f'untypical_result/result_{line}', imgcv)
                        #print(f"{img_name} : {lx}, {bot}, {rx}, {top}")
                    #############
                else:  ## groundtruth
                    labelinfos = []
                    
                    with open(os.path.join(boxtypeDir, f'{img_name}.box'), 'r') as f_gt:
                        labelinfos = f_gt.readlines()    
                    for labelinfo in labelinfos[1:]: 
                        try: 
                            label, lx, bot, rx, top, _ = map(str, labelinfo.strip().split())
                            if label not in classes: 
                                continue
                            lx, bot, rx, top = map(int, [lx, bot, rx, top])
                            conf = 1.0
                            boxinfo = [img_name, label, conf, (lx, bot, rx, top)]
                            groundtruths.append(boxinfo)
                        except: continue
            
    
    return detections, groundtruths  # inf, gt, class 정보


import cv2
if __name__ == "__main__": 
    model_name = 'Hangul2' #Hangul2 Letter2 Hangul Letter
    lang = 'kor_han2'  # ex) kor_han2 kor_letter2 kor_han kor_letter
    eval_dir = 'untypical_map_box' #labelPath
    gt_dir = 'untypical_map_img'  # imagePath
    extension = 'png'
    
    #####################################

    classes = []
    with open('ko.json', 'r') as f: 
        json_data = json.load(f)
        classes = json_data["words"]["character"]
    classes = sorted(classes)
    
    # gt는 이미 있다!
    detections, gts = [], []
    if model_name == 'rule': 
        detections, gts = n_divide_boundingBoxes(eval_dir, gt_dir, extension, classes)
        
    else: 
        eval_list = 'eval.txt'
        detections, gts = boundingBoxesUn(eval_dir, gt_dir , extension, classes, eval_list, lang)
    
    for detection in detections: 
        img_name, char, _, bbox = detection
        if os.path.exists(f'map_result/result_{model_name}_{img_name}.png'): 
            img = cv2.imread(f'map_result/result_{model_name}_{img_name}.png')
        else:     
            img = cv2.imread(os.path.join(gt_dir, img_name+'.png'))
        image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        x1, y1, x2, y2 = bbox
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 1)
        cv2.imwrite(f'map_result/result_{model_name}_{img_name}.png', image)
        
    
    result_ap = AP(detections, gts, classes)
    result_map = mAP(result_ap)
    print(f"untypical result map of {model_name} is {result_map}!!!")