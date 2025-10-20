import fitz
import re

# 지정된 PDF 페이지에서 문장을 추출하고, 소문자로 시작하는 문장을 합칩니다.
def extract_sentences_from_page(page):
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
    print(f"    - 분석 결과: {analysis_data}")

    for e in analysis_data:
        for key, value in e.items():
            print(f"Key: '{key}', Value: '{value}'")
        
            # for word, pos_tag in analysis_data:

            if not value or value == "None":
                continue

            # highlight_map에 POS 태그가 정의되어 있으면
            if value in highlight_map:
                details = highlight_map[value]
                description_text = details["desc_key"]

                try:
                    # PDF 내에서 해당 단어 검색
                    text_instances = page.search_for(key.strip(), flags=fitz.TEXT_PRESERVE_WHITESPACE)

                    if not text_instances:
                        print(f"    ⚠️ 경고: '{key}' 텍스트를 페이지에서 찾지 못했습니다.")
                        continue

                    for inst in text_instances:
                        # 이미 하이라이트된 영역 중복 방지
                        is_already_highlighted = any(inst.intersects(rect) for rect in existing_highlight_rects)
                        if is_already_highlighted:
                            print(f"    ⏭️ 건너뛰기: '{key}' 영역이 이미 다른 요소로 하이라이트 처리되었습니다.")
                            continue

                        # 하이라이트 생성
                        highlight = page.add_highlight_annot(inst)
                        highlight.set_colors(stroke=details["color"])
                        highlight.set_info(info={"content": description_text})
                        highlight.update()
                        existing_highlight_rects.append(inst)
                        print(f"    ✅ '{key}' ({value}) 하이라이트 완료.")
                        break  # 동일 단어의 첫 번째만 처리

                except Exception as e:
                    print(f"    ❌ '{key}' 하이라이트 중 오류 발생: {e}")
            else:
                # highlight_map에 정의되지 않은 품사는 건너뜀
                pass