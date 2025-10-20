import os
import fitz
import ast
from google import genai
from dotenv import load_dotenv

from geminiapi import analyze_sentence_with_gemini
import editpdf
# from editpdf import extract_sentences_from_page, apply_highlights_to_page
from spacy_analyzer import analysis_sentence_ingredients

load_dotenv()

# --- 설정 불러오기 ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
INPUT_PDF_PATH = os.getenv("INPUT_PDF_PATH")
OUTPUT_PDF_PATH = os.getenv("OUTPUT_PDF_PATH")
START_PAGE = int(os.getenv("START_PAGE"))
END_PAGE = int(os.getenv("END_PAGE"))

# .env에서 문자열로 저장된 색상 값을 튜플로 변환하는 함수
def parse_color(color_str):
    return tuple(map(float, color_str.split(',')))

# 색상 및 하이라이트 맵 설정 (기본 성분 그룹, 품사 그룹, 동사 확장 그룹, 구조 단위 그룹, 수식어 그룹)
HIGHLIGHT_MAP = {
    "NN": {"color": parse_color(os.getenv("RED")), "desc_key": "단수명사, "},
    "NNS": {"color": parse_color(os.getenv("RED")), "desc_key": "복수명사, "},
    "NNP": {"color": parse_color(os.getenv("RED")), "desc_key": "단수 고유명사, "},
    "NNPS": {"color": parse_color(os.getenv("RED")), "desc_key": "복수 고유명사, "},
    "PRP": {"color": parse_color(os.getenv("RED")), "desc_key": "인칭대명사, "},
    "PRP$": {"color": parse_color(os.getenv("RED")), "desc_key": "소유대명사, "},
    "WDT": {"color": parse_color(os.getenv("RED")), "desc_key": "의문명사, "},
    "WP": {"color": parse_color(os.getenv("RED")), "desc_key": "의문대명사, "},

    "MD": {"color": parse_color(os.getenv("ORANGE")), "desc_key": "조동사, "},
    "VB": {"color": parse_color(os.getenv("ORANGE")), "desc_key": "동사, "},
    "VBG": {"color": parse_color(os.getenv("ORANGE")), "desc_key": "동명사, "},
    "VBD": {"color": parse_color(os.getenv("ORANGE")), "desc_key": "동사(과거완료), "},
    "VBN": {"color": parse_color(os.getenv("ORANGE")), "desc_key": "과거분사, "},
    "VBP": {"color": parse_color(os.getenv("ORANGE")), "desc_key": "동사(3인칭 단수가 아닌 현재시제), "},
    "VBZ": {"color": parse_color(os.getenv("ORANGE")), "desc_key": "동사(3인칭 단수인 현재시제), "},
    "TO": {"color": parse_color(os.getenv("ORANGE")), "desc_key": "to부정사, "},

    "JJ": {"color": parse_color(os.getenv("YELLOW")), "desc_key": "형용사(원급), "},
    "JJR": {"color": parse_color(os.getenv("YELLOW")), "desc_key": "형용사(비교급), "},
    "JJS": {"color": parse_color(os.getenv("YELLOW")), "desc_key": "형용사(최상급), "},

    "CC": {"color": parse_color(os.getenv("GREEN")), "desc_key": "등위 접속사, "},

    "IN": {"color": parse_color(os.getenv("BLUE")), "desc_key": "전치사/종속접속사, "},
    "RP": {"color": parse_color(os.getenv("BLUE")), "desc_key": "조사, "},
    
    "RB": {"color": parse_color(os.getenv("NAVY")), "desc_key": "부사(원급), "},
    "RBR": {"color": parse_color(os.getenv("NAVY")), "desc_key": "부사(비교급), "},
    "RBS": {"color": parse_color(os.getenv("NAVY")), "desc_key": "부사(최상급), "},
    "WRB": {"color": parse_color(os.getenv("NAVY")), "desc_key": "의문부사, "},

    "DT": {"color": parse_color(os.getenv("PURPLE")), "desc_key": "한정사, "},
    "PDT": {"color": parse_color(os.getenv("PURPLE")), "desc_key": "전치한정사, "},

    "CD": {"color": parse_color(os.getenv("SKY")), "desc_key": "숫자, "},
    "EX": {"color": parse_color(os.getenv("SKY")), "desc_key": "존재 표현, "},
    "FW": {"color": parse_color(os.getenv("SKY")), "desc_key": "외래어, "},
    "LS": {"color": parse_color(os.getenv("SKY")), "desc_key": "나열 목록, "},
    "POS": {"color": parse_color(os.getenv("SKY")), "desc_key": "소유격, "},
    "UH": {"color": parse_color(os.getenv("SKY")), "desc_key": "감탄사, "}
}

def main():
    """메인 실행 함수"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        print("❌ 오류: .env 파일에 'GEMINI_API_KEY'를 설정해주세요.")
        return

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"❌ Gemini 클라이언트 초기화 실패: {e}")
        return

    try:
        doc = fitz.open(INPUT_PDF_PATH)
        print(f"🚀 PDF 파일 '{INPUT_PDF_PATH}'을 열었습니다. 총 {len(doc)} 페이지.")
    except FileNotFoundError:
        print(f"❌ 오류: '{INPUT_PDF_PATH}' 파일을 찾을 수 없습니다.")
        return
    except Exception as e:
        print(f"❌ PDF 파일을 여는 중 오류 발생: {e}")
        return

    if not (1 <= START_PAGE <= END_PAGE <= len(doc)):
        print(f"❌ 오류: 페이지 범위가 잘못되었습니다. (1 ~ {len(doc)} 사이로 지정해주세요)")
        doc.close()
        return

    for page_num in range(START_PAGE, END_PAGE + 1):
        print(f"\n📄 {page_num} 페이지 분석을 시작합니다...")
        current_page = doc[page_num - 1]
        page_highlight_rects = [annot.rect for annot in current_page.annots() if annot.type[1] == 'Highlight']
        sentences = editpdf.extract_sentences_from_page(current_page)
        
        if not sentences:
            print("  - 해당 페이지에서 문장을 찾을 수 없습니다.")
            continue
            
        print(f"  - {len(sentences)}개의 문장을 추출했습니다.")

        for sentence in sentences:
            print(f"\n  ▶️ 문장 분석 요청: \"{sentence}\"")
            analysis_result = analysis_sentence_ingredients(sentence) # 단어별 문장 분석 진행
            print(type(analysis_result))

            grouped_data = editpdf.grouping_data(analysis_result) # 서로 붙어있는 품사일 때에는 하나로 병합
            print(grouped_data)
            # 그룹화된 성분별 번역 진행
            translated_analysis_result = analyze_sentence_with_gemini(grouped_data, page_num, client)

            # 번역된 것을 list type으로 변경함
            list_translated_final = ast.literal_eval(translated_analysis_result)

            # analysis_result = analyze_sentence_with_gemini(sentence, page_num, client)
            # print(type(analysis_result))

            if analysis_result:
                editpdf.apply_highlights_to_page(current_page, grouped_data, list_translated_final, page_highlight_rects, HIGHLIGHT_MAP)
            else:
                print("  - 이 문장에 대한 분석 결과를 받지 못해 하이라이트를 건너뜁니다.")

    try:
        doc.save(OUTPUT_PDF_PATH)
        print(f"\n\n🎉 모든 작업이 완료되었습니다. 결과가 '{OUTPUT_PDF_PATH}' 파일에 저장되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 결과 파일을 저장하는 중 오류 발생: {e}")
    finally:
        doc.close()

if __name__ == "__main__":
    main()