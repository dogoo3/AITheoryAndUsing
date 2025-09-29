import fitz
import re

def extract_sentences_from_page(page):
    """지정된 PDF 페이지에서 문장을 추출하고, 소문자로 시작하는 문장을 합칩니다."""
    text = page.get_text("text")
    processed_text = re.sub(r'(?<=[^\.])\n', ' ', text)
    sentences = re.split('(?<=[.?!])\s*', processed_text)

    combined_sentences = []
    if sentences:
        current_sentence = sentences[0].strip()
        for i in range(1, len(sentences)):
            next_sentence = sentences[i].strip()
            if next_sentence:
                if next_sentence[0].islower():
                    current_sentence += " " + next_sentence
                else:
                    combined_sentences.append(current_sentence)
                    current_sentence = next_sentence
        if current_sentence:
            combined_sentences.append(current_sentence)

    return [s for s in combined_sentences if s]

def apply_highlights_to_page(page, analysis_data, existing_highlight_rects, highlight_map):
    """분석된 JSON 데이터를 기반으로 PDF 페이지에 하이라이트를 적용합니다."""
    print(f"    - 분석 결과: {analysis_data}")
    for component, details in highlight_map.items():
        component_text = analysis_data.get(component)
        description_text = analysis_data.get(details["desc_key"])

        if component_text and description_text:
            try:
                text_instances = page.search_for(component_text.strip(), flags=fitz.TEXT_PRESERVE_WHITESPACE)
                
                if not text_instances:
                    print(f"    ⚠️ 경고: '{component_text}' 텍스트를 페이지에서 찾지 못했습니다.")
                    continue

                for inst in text_instances:
                    is_already_highlighted = False
                    for existing_rect in existing_highlight_rects:
                        if inst.intersects(existing_rect):
                            is_already_highlighted = True
                            print(f"    ⏭️ 건너뛰기: '{component_text}' 영역이 이미 다른 요소로 하이라이트 처리되었습니다.")
                            break 
                    
                    if not is_already_highlighted:
                        highlight = page.add_highlight_annot(inst)
                        highlight.set_colors(stroke=details["color"])
                        highlight.set_info(info={"content": description_text})
                        highlight.update()
                        existing_highlight_rects.append(inst)
                        print(f"    ✅ '{component}' ({component_text}) 하이라이트 완료.")
                        break

            except Exception as e:
                print(f"    ❌ '{component_text}' 하이라이트 중 오류 발생: {e}")