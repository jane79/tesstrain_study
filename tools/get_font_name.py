import os

font_list = './font_list.txt'
exclude_font_list = './exclude_font_list.txt'  # 이미 데이터셋을 만들어서 다시 만들 필요 없는 폰트 리스트
f = open(font_list, 'r')
fonts_info = f.readlines()
f.close()
f = open(exclude_font_list, 'r')
exclude_fonts = f.readlines()
for i, exclude_font in enumerate(exclude_fonts): 
    exclude_fonts[i] = exclude_font.strip()
f.close()

with open('./result_font_list.txt', 'w') as f2: 
    for font_info in fonts_info: 
        name = font_info.split(':')[-1]
        name = name.strip()
        if name not in exclude_fonts: 
            name = "\"" + name + "\" "
            f2.write(name)
    print("DONE!")
        