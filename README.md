설치~학습 전체적인 흐름은 tesstrain readme를 따른다

[GitHub - tesseract-ocr/tesstrain: Train Tesseract LSTM with make](https://github.com/tesseract-ocr/tesstrain)

# Installation

1. [tesstrain](https://github.com/tesseract-ocr/tesstrain) 을 git clone 한다.
2. 우선적으로 설치해야 할 것들 **꼭 먼저 설치하기!!!**
    
    ![image](https://user-images.githubusercontent.com/48004826/231050848-2b86b450-c4ee-4093-9f85-8ff18985527d.png)
    - automake
    - pkg-config
    - pango-devel
    - cairo-devel
    - icu-devel
    - rename
3. tesseract 및 leptonica를 build한다.

```python
$ cd tesstrain
$ make leptonica tesseract
## tesseract build
$ cd tesseract-5.3.0
$ ./autogen.sh
$ ./configure
$ make
$ sudo make install
$ sudo ldconfig
$ make training
$ sudo make training-install
## leptonica build
$ cd ..
$ cd leptonica-1.83.0
$ ./autogen.sh
$ ./configure
$ make
$ sudo make install
$ sudo ldconfig
```

- 위와 같은 과정은 [여기](https://github.com/tesseract-ocr/tesseract/blob/main/INSTALL.GIT.md)에 적혀있다

혹시 `make training` 도중 `filesystem: No such file or directory`와 같은 에러 메시지가 뜬다면,

1) gcc 버전 확인 2) 8보다 낮다면 아래 글을 참고하여 gcc 버전 업데이트하자

[[해결법] fatal error: filesystem: No such file or directory](https://jtrimind.github.io/troubleshooting/filesystem/)

4. `$ pip install -r requirements.txt`
5. `$ make tesseract-langdata`

# Prepare Training Dataset

1. 학습할 폰트를 우분투에 설치한다.

`sudo apt install fontconfig`

`/usr/share/fonts/`에 학습 폰트 파일을 위치시킨 뒤

`sudo fc-cache -f -v`

[리눅스 폰트(linux font) 설치 및 font config 사용법](https://www.lesstif.com/lpt/linux-font-font-config-93127497.html)

2. 학습 폰트 리스트를 추출한다.

우분투에서 인식하는 폰트명이 복수개일 때가 있는데, tesstrain이 모두를 인식하진 못하는 것을 확인했다. 따라서 tesstrain에서 인식하는 폰트명을 우선 추출하고 난 후, 그것을 tesstrain 파라미터로 입력해야 한다. 즉 fontlist엔 text2image 실행 시 출력되는 폰트 명을 적어주어야 한다! (자세한건 [이슈](https://github.com/tesseract-ocr/tesseract/issues/217) 참조)

```python
$ cd src
$ text2image --list_available_fonts --fonts_dir 폰트경로 
# 폰트 경로 내 학습에 사용 가능한 폰트의 명칭을 가져옴
# 커맨드에 출력되는 결과를 tools/font_list.txt에 붙여넣기
# 이미 데이터셋을 생성하여 재생성할 필요가 없는 폰트는 tools/exclude_font_list.txt에 적어주기
$ python ../tools/get_font_name.py
# tesstrain의 fontlist 인자 값으로 가능한 폰트 명칭들이 result_font_list.txt 에 저장됨
```

3. tesstrain으로 학습 데이터셋을 생성한다.

tesstrain.py로 학습 데이터셋 생성 전 필요한 사전작업을 한다. 예시 코드 및 예시 사전 작업은 아래에서 확인할 수 있다.

```python

$ python -m tesstrain \
--fontlist `result_font_list.txt`에 적힌 내용 \
--fonts_dir /opt/level3_productserving-level3-cv-11/data/fonts/untypical \
--lang kor \
--langdata_dir /opt/level3_productserving-level3-cv-11/model/tesstrain/data/langdata \
--output_dir /opt/level3_productserving-level3-cv-11/model/tesstrain/data/Hangul-ground-truth \
--save_box_tiff \
--noextract_font_properties \
--linedata_only \
--tessdata_dir /opt/level3_productserving-level3-cv-11/model/tesstrain/usr/share/tessdata
```

인자에 대한 설명은 `python -m tesstrain --help` 로 확인할 수 있다.

- `data/langdata/kor` 내에 [tesseract-ocr](https://github.com/tesseract-ocr/langdata/tree/main/kor) 의 파일을 모두 다운 받아서 넣어 준다.
- training_text 는 자동적으로 langdata 내부의 training_text 파일로 지정되는데, 따로 지정해주고 싶으면 `--training_text`로 전달해주면 된다.
- `usr/share/tessdata`에 traineddata (from [tessdata_best](https://github.com/tesseract-ocr/tessdata_best)) 를 저장한다.
- output_dir에 box, tif가 저장된다. tif 가 바로 생성된 학습 데이터셋이다.

tesseract 의 traineddata 및 training_text 파일을 사용하여 학습 데이터셋을 생성했을 경우, 다음과 같은 문제로 인해 **바로 tesseract 모델 학습에 사용할 순 없다.**

1. tif 파일은 단일이 아니라 사실 여러개의 페이지로 저장되어 있다. training_text가 한 페이지에 담아내기엔 너무 길기 때문이다. (첫 페이지만 보이는 vs code extension 이 있어 단일 사진 파일로 착각할 수 있다)
2. tif 파일의 각 페이지엔 여러 줄의 글이 적혀있다. tesseract 학습용 데이터셋은 단일 줄글이어야 한다.

즉 학습에 사용 하기 위해선 다음과 같은 작업이 필요하다.

1. tif 파일을 페이지 단위로 분할
    
    `/opt/level3_productserving-level3-cv-11/model/tesstrain/data/split_tif.py` 실행 ([코드 출처](https://stackoverflow.com/questions/21340740/split-tif-file-using-pil)).
    
    분할 이전 tif 파일이 저장된 폴더가 imgs_root, 분할된 파일이 저장될 폴더가 gt_root여야 함.
    
2. 분할된 페이지별 텍스트를 한 줄 글 이미지로 분할
    
    tesstrain은 한 줄 텍스트만 학습 데이터로 사용할 수 있기 때문. 따라서 한 줄 씩 분리된 이미지 및 gt를 저장해야 한다. 
    
    [이슈](https://github.com/tesseract-ocr/tesstrain/issues/7)의 Shreeshrii 코멘트를 보면,
    
    a. `$ git clone [https://github.com/ocropus/hocr-tools.git](https://github.com/ocropus/hocr-tools.git)` 및 리드미의 installation 따르기  
    b. 클론한 레포에서 다음 내용의 sh 파일 작성 및 실행
        
        ```python
        #!/bin/bash
        SOURCE="./myfiles/"
        lang=san
        set -- "$SOURCE"*.png
        for img_file; do
            echo -e  "\r\n File: $img_file"
            OMP_THREAD_LIMIT=1 tesseract --tessdata-dir ../tessdata_fast   "${img_file}" "${img_file%.*}"  --psm 6  --oem 1  -l $lang -c page_separator='' hocr
            #source venv/bin/activate
            PYTHONIOENCODING=UTF-8 ./hocr-extract-images -b ./myfiles/ -p "${img_file%.*}"-%03d.exp0.tif  "${img_file%.*}".hocr 
            #deactivate
        done
        rename s/exp0.txt/exp0.gt.txt/ ./myfiles/*exp0.txt
        
        echo "Image files converted to tif. Correct the ground truth files and then run ocr-d train to create box and lstmf files"
        ```
        
        그러면 LANG.FONTNAME_page_%d-%03d.tif/gt 파일이 생성될 것. 각 파일은 kor.training_text 한 줄에 대한 정보를 담고 있다. 만약 **rename이 안 되었을 경우 터미널에서 rename만 다시 실행**  
        
    c. `mv_multiline_to_tmp.py` 를 실행하여 기존의 여러 줄의 텍스트가 포함된 파일들을 임시 폴더(tmp)로 옮김. 삭제해도 상관 X  
    d. `update_gt.py`로 .gt 파일들의 내용을 정정해준다. 무슨 이유에선지 손실된 줄이 있거나, 한 페이지에 동일 개수의 줄이 들어있지 않은 특정 폰트가 있었다. (아래 이미지 참조) 이들은 일단은 학습 데이터에서 제외했다. (Hangul-ground-truth-wrong으로 옮김)  

    ![image](https://user-images.githubusercontent.com/48004826/231051474-f6151284-ddb4-4002-95d0-fc3e67056ccd.png)
        

# Training

```python
make training MODEL_NAME=Hangul \
LEPTONICA_VERSION=1.83.0 \
TESSERACT_VERSION=5.3.0 \
NUMBERS_FILE=/opt/level3_productserving-level3-cv-11/model/tesstrain/data/langdata/kor/kor.numbers \
PUNC_FILE=/opt/level3_productserving-level3-cv-11/model/tesstrain/data/langdata/kor/kor.punc \
WORLDSLIST_FILE=/opt/level3_productserving-level3-cv-11/model/tesstrain/data/langdata/kor/kor.wordlist \
START_MODEL=kor
```

실행 후 아래 사진과 같은 에러 혹은 encoding error가 쭉 뜰 경우, all-gt 파일이 비어있는지 확인

![image](https://user-images.githubusercontent.com/48004826/231051587-79f3a1de-afb4-4d83-8b36-07e747623a1a.png)

비어있을 경우, 아래 해결 방법 사용

tesstrain/Makefile line 220 : $(**file** >$@) $(**foreach** F,$^,$(**file** >>$@,$(**file** <$F)))

![image](https://user-images.githubusercontent.com/48004826/231051670-2ede6050-085e-4bbe-bd9c-8bb26fc4d8b6.png)

`<` operator는 make 4.2 버전 이상에서.. 하지만 make를 4.2로 업그레이드 하고 training 실행할 경우 segmentation fault (core dumped)가 발생한다. 그럼 어떻게?

 ⇒ `$(**file** >$@) $(**foreach** F,$^,$(**file** >>$@,$(**shell** cat $F)))` 로 수정, [참고](https://stackoverflow.com/questions/40861311/how-can-i-read-a-file-using-makes-file-function)

학습 결과로 traineddata 모델 만들기, 자세한 사항은 [tesstrain 리드미](https://github.com/tesseract-ocr/tesstrain) 참고
