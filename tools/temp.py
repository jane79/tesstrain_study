import os

usr_fonts_dir = '/usr/share/fonts/'
usr_fonts = os.listdir(usr_fonts_dir)
target_fonts_dir = '/opt/test/GAS-NeXt/datasets/ttfs/untypical'
target_fonts = os.listdir(target_fonts_dir)

difference = []
for font in usr_fonts: 
    if font not in target_fonts: 
        difference.append(font)
#print(target_fonts)
#print("differences :", difference)

old_fonts_dir = '/opt/level3_productserving-level3-cv-11/data/fonts/untypical'
print(os.listdir(old_fonts_dir))