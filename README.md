# AI Theory and Using

# 주요 기능
* 영문으로 작성된 PDF에서 원하는 페이지의 문장을 성분 분석할 수 있습니다.

# 시작하기
1. Repository를 Clone합니다.
```python
git clone https://github.com/dogoo3/AITheoryAndUsing.git
```

2. main.py가 위치한 곳에 아래 코드와 같이 .env를 생성합니다.
```python
# Gemini API Key
# You must need modify below attribute.
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

# PDF File Paths
INPUT_PDF_PATH="highlight_before.pdf"
OUTPUT_PDF_PATH="test_output.pdf"

# Page Range
START_PAGE=1
END_PAGE=1

# Color Variables (R, G, B)
RED="1, 0, 0"
ORANGE="1, 0.647, 0"
YELLOW="1, 1, 0"
GREEN="0, 1, 0"
BLUE="0, 0, 1"
PURPLE="0.698, 0.047, 1"
SKY="0, 1, 0.866"
MAGENTA="1, 0, 1"
```

3. 필요한 패키지를 설치해 줍니다.
```python
pip install -r requirements.txt
```

# 업데이트 정보
* 1.0 새 Repository를 생성했습니다.

Acknowledgements
-
This project uses PyMuPDF (https://github.com/pymupdf/PyMuPDF),
which is licensed under the GNU General Public License v3.0.
