from PIL import Image
from tqdm import tqdm
import os

imgs_root = './Hangul2-ground-truth-tmp'
gt_root = './Hangul2-ground-truth'
images = os.listdir(imgs_root)
for image in tqdm(images): 
    if image.split('.')[-1] == 'tif': 
        img = Image.open(os.path.join(imgs_root, image))
        for i in range(1000):
            try:
                img.seek(i)
                name = ".".join(image.split('.')[:-2])
                img.save('%s/%s_page_%s.tif'%(gt_root, name, i))
            except EOFError:
                break