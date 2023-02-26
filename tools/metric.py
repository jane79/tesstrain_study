import json
import os
import cv2
import pytesseract

from bs4 import BeautifulSoup
import subprocess
import numpy as np
from tqdm import tqdm

## GET BB INFO : detections, gts
def boundingBoxes(labelPath, imagePath, extension, classes, evalList, lang):   # Letter2-eval  
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
                    with open(os.path.join(boxtypeDir, f'{img_name}.box'), 'w') as f_dt: 
                        for cinfo in cinfos: 
                            label = cinfo.text
                            bbox, x_conf = cinfo['title'].split(';')
                            lx, bot, rx, top = map(int, bbox.strip().split()[1:])
                            f_dt.write(f'{label} {lx} {bot} {rx} {top}\n')
                            conf = float(x_conf.strip().split()[-1])
                            boxinfo = [img_name, label, conf, (lx, bot, rx, top)]
                            detections.append(boxinfo)
                else:  ## groundtruth
                    labelinfos = []
                    
                    with open(os.path.join(boxtypeDir, f'{img_name}.box'), 'r') as f_gt:
                        labelinfos = f_gt.readlines()    
                    for labelinfo in labelinfos: 
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



## GET IOU
def getArea(box):
    return (box[2] - box[0]) * (box[3] - box[1])

def getIntersectionArea(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    # intersection area
    return (xB - xA) * (yB - yA)

def getUnionAreas(boxA, boxB, interArea=None):
    area_A = getArea(boxA)
    area_B = getArea(boxB)
    if interArea is None:
        interArea = getIntersectionArea(boxA, boxB)
    return float(area_A + area_B - interArea)

def boxesIntersect(boxA, boxB):  # 겹치는지 확인
    if boxA[0] > boxB[2]:
        return False  # boxA is right of boxB
    if boxB[0] > boxA[2]:
        return False  # boxA is left of boxB
    if boxA[3] < boxB[1]:
        return False  # boxA is above boxB
    if boxA[1] > boxB[3]:
        return False  # boxA is below boxB
    return True

def iou(boxA, boxB):
    # if boxes dont intersect
    if boxesIntersect(boxA, boxB) is False:
        return 0
    interArea = getIntersectionArea(boxA, boxB)
    union = getUnionAreas(boxA, boxB, interArea=interArea)
    # intersection over union
    result = interArea / union
    assert result >= 0
    return result



## GET PR GRAPH
def ElevenPointInterpolatedAP(rec, prec):
    mrec = [e for e in rec]
    mpre = [e for e in prec]
    # recallValues = [1.0, 0.9, ..., 0.0]
    recallValues = np.linspace(0, 1, 11)
    recallValues = list(recallValues[::-1])
    rhoInterp, recallValid = [], []
    for r in recallValues:
        # r : recall값의 구간
        # argGreaterRecalls : r보다 큰 값의 index
        argGreaterRecalls = np.argwhere(mrec[:] >= r)
        pmax = 0
        print(r, argGreaterRecalls)
        # precision 값 중에서 r 구간의 recall 값에 해당하는 최댓값
        if argGreaterRecalls.size != 0:
            pmax = max(mpre[argGreaterRecalls.min():])
        recallValid.append(r)
        rhoInterp.append(pmax)
    ap = sum(rhoInterp) / 11
    return [ap, rhoInterp, recallValues, None]


def calculateAveragePrecision(rec, prec):
    mrec = [0] + [e for e in rec] + [1]
    mpre = [0] + [e for e in prec] + [0]
    for i in range(len(mpre)-1, 0, -1):
        mpre[i-1] = max(mpre[i-1], mpre[i])
    ii = []
    for i in range(len(mrec)-1):
        if mrec[1:][i] != mrec[0:-1][i]:
            ii.append(i+1)
    ap = 0
    for i in ii:
        ap = ap + np.sum((mrec[i] - mrec[i-1]) * mpre[i])
    return [ap, mpre[0:len(mpre)-1], mrec[0:len(mpre)-1], ii]

def ElevenPointInterpolatedAP(rec, prec):
    mrec = [e for e in rec]
    mpre = [e for e in prec]
    recallValues = np.linspace(0, 1, 11)
    recallValues = list(recallValues[::-1])
    rhoInterp, recallValid = [], []
    for r in recallValues:
        argGreaterRecalls = np.argwhere(mrec[:] >= r)
        pmax = 0
        if argGreaterRecalls.size != 0:
            pmax = max(mpre[argGreaterRecalls.min():])
        recallValid.append(r)
        rhoInterp.append(pmax)
    ap = sum(rhoInterp) / 11
    return [ap, rhoInterp, recallValues, None]


from collections import Counter
## GET AP
def AP(detections, groundtruths, classes, IOUThreshold = 0.3, method = 'AP'):
    # 클래스별 AP, Precision, Recall 등 관련 정보를 저장할 리스트
    result = []
    # 클래스별로 접근
    for c in classes:
        # 특정 class에 해당하는 box를 box타입(detected, ground truth)에 따라 분류
        dects = [d for d in detections if d[1] == c]
        gts = [g for g in groundtruths if g[1] == c]
        # 전체 ground truth box의 수
        # Recall 값의 분모
        npos = len(gts)
        # confidence score에 따라 내림차순 정렬
        dects = sorted(dects, key = lambda conf : conf[2], reverse=True)
        TP = np.zeros(len(dects))
        FP = np.zeros(len(dects))
        # 각 이미지별 ground truth box의 수
        # {99 : 2, 380 : 4, ....}
        det = Counter(cc[0] for cc in gts)
        # {99 : [0, 0], 380 : [0, 0, 0, 0], ...}
        for key, val in det.items():
            det[key] = np.zeros(val)
        
         # 전체 detected box
        for d in range(len(dects)):
            # ground truth box 중에서 detected box와 같은 이미지 파일에 존재하는 box
            # dects[d][0] : 이미지 파일명
            gt = [gt for gt in gts if gt[0] == dects[d][0]]
            iouMax = 0
            # 하나의 detected box에 대하여 같은 이미지에 존재하는 모든 ground truth 값을 비교
            # 가장 큰 IoU 값을 가지는 하나의 ground truth box에 매칭
            for j in range(len(gt)):
                iou1 = iou(dects[d][3], gt[j][3])
                if iou1 > iouMax:
                    iouMax = iou1
                    jmax = j
            # IoU 임계값 이상 and ground truth box가 매칭되지 않음 => TP
            # IoU 임계값 미만 or ground truth box가 다른 detected box에 이미 매칭됨 => FP
            if iouMax >= IOUThreshold:
                if det[dects[d][0]][jmax] == 0:
                    TP[d] = 1
                    det[dects[d][0]][jmax] = 1
                else:
                    FP[d] = 1
            else:
                FP[d] = 1
        # Precision, Recall 값을 구하기 위한 누적 TP, FP
        acc_FP = np.cumsum(FP)
        acc_TP = np.cumsum(TP)
        rec = acc_TP / npos
        prec = np.divide(acc_TP, (acc_FP + acc_TP))
        if method == "AP":
            [ap, mpre, mrec, ii] = calculateAveragePrecision(rec, prec)
        else:
            [ap, mpre, mrec, _] = ElevenPointInterpolatedAP(rec, prec)
        r = {
            'class' : c,
            'precision' : prec,
            'recall' : rec,
            'AP' : ap,
            'interpolated precision' : mpre,
            'interpolated recall' : mrec,
            'total positives' : npos,
            'total TP' : np.sum(TP),
            'total FP' : np.sum(FP)
        }
        result.append(r)
    return result



def mAP(result):
    ap = 0
    classes_num = len(result)
    #with open('log.txt', 'w') as f: 
    for r in result:
        if np.isnan(r['AP']) or len(r['precision']) == 0:
            classes_num -= 1
            continue
        ap += r['AP']
        #f.write(f"누적 ap : {ap}, ap : {r['AP']}\n")
    mAP = ap / classes_num
    return mAP


# https://herbwood.tistory.com/3
# https://github.com/herbwood/mAP/blob/main/mAP.ipynb