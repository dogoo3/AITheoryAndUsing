import os
import fitz
from google import genai
from dotenv import load_dotenv

from geminiapi import analyze_sentence_with_gemini
from editpdf import extract_sentences_from_page, apply_highlights_to_page

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

# 색상 및 하이라이트 맵 설정
HIGHLIGHT_MAP = {
    "subject": {"color": parse_color(os.getenv("RED")), "desc_key": "subject_desc"},
    "verb": {"color": parse_color(os.getenv("RED")), "desc_key": "verb_desc"},
    "objective": {"color": parse_color(os.getenv("RED")), "desc_key": "objective_desc"},
    "complement": {"color": parse_color(os.getenv("RED")), "desc_key": "complement_desc"},
    "noun": {"color": parse_color(os.getenv("ORANGE")), "desc_key": "noun_desc"},
    "adjective": {"color": parse_color(os.getenv("ORANGE")), "desc_key": "adjective_desc"},
    "adverb": {"color": parse_color(os.getenv("ORANGE")), "desc_key": "adverb_desc"},
    "article": {"color": parse_color(os.getenv("ORANGE")), "desc_key": "article_desc"},
    "determiner": {"color": parse_color(os.getenv("ORANGE")), "desc_key": "determiner_desc"},
    "preposition": {"color": parse_color(os.getenv("ORANGE")), "desc_key": "preposition_desc"},
    "conjunction": {"color": parse_color(os.getenv("ORANGE")), "desc_key": "conjunction_desc"},
    "interrogative": {"color": parse_color(os.getenv("ORANGE")), "desc_key": "interrogative_desc"},
    "relative_pronoun": {"color": parse_color(os.getenv("ORANGE")), "desc_key": "relative_pronoun_desc"},
    "modal": {"color": parse_color(os.getenv("YELLOW")), "desc_key": "modal_desc"},
    "auxiliary": {"color": parse_color(os.getenv("YELLOW")), "desc_key": "auxiliary_desc"},
    "gerund": {"color": parse_color(os.getenv("YELLOW")), "desc_key": "gerund_desc"},
    "participle": {"color": parse_color(os.getenv("YELLOW")), "desc_key": "participle_desc"},
    "infinitive": {"color": parse_color(os.getenv("YELLOW")), "desc_key": "infinitive_desc"},
    "prepositional_phrase": {"color": parse_color(os.getenv("GREEN")), "desc_key": "prepositional_phrase_desc"},
    "clause": {"color": parse_color(os.getenv("GREEN")), "desc_key": "clause_desc"},
    "phrase": {"color": parse_color(os.getenv("GREEN")), "desc_key": "phrase_desc"},
    "modifier": {"color": parse_color(os.getenv("SKY")), "desc_key": "modifier_desc"}
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
        sentences = extract_sentences_from_page(current_page)
        
        if not sentences:
            print("  - 해당 페이지에서 문장을 찾을 수 없습니다.")
            continue
            
        print(f"  - {len(sentences)}개의 문장을 추출했습니다.")

        for sentence in sentences:
            print(f"\n  ▶️ 문장 분석 요청: \"{sentence}\"")
            analysis_result = analyze_sentence_with_gemini(sentence, page_num, client)
            
            if analysis_result:
                apply_highlights_to_page(current_page, analysis_result, page_highlight_rects, HIGHLIGHT_MAP)
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