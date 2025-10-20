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

# def apply_highlights_to_page(page, analysis_data, existing_highlight_rects, highlight_map):
#     print(f"    - 분석 결과: {analysis_data}")

#     for e in analysis_data:
#         for key, value in e.items():
#             print(f"Key: '{key}', Value: '{value}'")
        
#             # for word, pos_tag in analysis_data:

#             if not value or value == "None":
#                 continue

#             # highlight_map에 POS 태그가 정의되어 있으면
#             if value in highlight_map:
#                 details = highlight_map[value]
#                 description_text = details["desc_key"]

#                 try:
#                     # PDF 내에서 해당 단어 검색
#                     text_instances = page.search_for(key.strip(), flags=fitz.TEXT_PRESERVE_WHITESPACE)

#                     if not text_instances:
#                         print(f"    ⚠️ 경고: '{key}' 텍스트를 페이지에서 찾지 못했습니다.")
#                         continue

#                     for inst in text_instances:
#                         # 이미 하이라이트된 영역 중복 방지
#                         is_already_highlighted = any(inst.intersects(rect) for rect in existing_highlight_rects)
#                         if is_already_highlighted:
#                             print(f"    ⏭️ 건너뛰기: '{key}' 영역이 이미 다른 요소로 하이라이트 처리되었습니다.")
#                             continue

#                         # 하이라이트 생성
#                         highlight = page.add_highlight_annot(inst)
#                         highlight.set_colors(stroke=details["color"])
#                         highlight.set_info(info={"content": description_text})
#                         highlight.update()
#                         existing_highlight_rects.append(inst)
#                         print(f"    ✅ '{key}' ({value}) 하이라이트 완료.")
#                         break  # 동일 단어의 첫 번째만 처리

#                 except Exception as e:
#                     print(f"    ❌ '{key}' 하이라이트 중 오류 발생: {e}")
#             else:
#                 # highlight_map에 정의되지 않은 품사는 건너뜀
#                 pass

def grouping_data(analysis_data):
    # --- 그룹화 로직 시작 ---

    # 1. 품사(POS) 태그를 그룹으로 매핑하는 딕셔너리를 정의합니다.
    pos_to_group = {
        'NN': '명사', 'NNS': '명사', 'NNP': '명사', 'NNPS': '명사', 'PRP': '명사', 'PRP$': '명사', 'WDT': '명사', 'WP': '명사',
        'MD': '동사', 'VB': '동사', 'VBG': '동사', 'VBD': '동사', 'VBN': '동사', 'VBP': '동사', 'VBZ': '동사', 'TO': '동사',
        'JJ': '형용사', 'JJR': '형용사', 'JJS': '형용사',
        'CC': '접속사',
        'IN': '전치사', 'RP': '전치사',
        'RB': '부사', 'RBR': '부사', 'RBS': '부사', 'WRB': '부사',
        'DT': '한정사', 'PDT': '한정사',
        'CD': '기타', 'EX': '기타', 'FW': '기타', 'LS': '기타', 'POS': '기타', 'UH': '기타'
    }

    # 2. 분석된 데이터를 순회하며 동일 그룹의 인접 단어를 병합합니다.
    grouped_analysis_data = []
    i = 0
    while i < len(analysis_data):
        # 현재 단어와 태그를 가져옵니다.
        current_item = analysis_data[i]
        current_word = list(current_item.keys())[0]
        current_tag = list(current_item.values())[0]

        # 현재 태그가 그룹에 속하는지 확인합니다.
        current_group = pos_to_group.get(current_tag)

        # 그룹에 속하고, 다음 단어가 있다면 그룹화를 시도합니다.
        if current_group:
            j = i + 1
            # 다음 단어가 같은 그룹에 속하는 동안 반복합니다.
            while j < len(analysis_data):
                next_item = analysis_data[j]
                next_word = list(next_item.keys())[0]
                next_tag = list(next_item.values())[0]
                next_group = pos_to_group.get(next_tag)

                if next_group == current_group:
                    # 같은 그룹이면 단어를 합치고 다음 단어로 넘어갑니다.
                    current_word += " " + next_word
                    j += 1
                else:
                    # 다른 그룹이면 중단합니다.
                    break
            
            # 그룹화된 결과를 새로운 리스트에 추가합니다.
            grouped_analysis_data.append({current_word: current_tag})
            # 인덱스를 병합된 단어의 수만큼 점프시킵니다.
            i = j
        else:
            # 그룹에 속하지 않는 단어(예: 구두점)는 그대로 추가합니다.
            grouped_analysis_data.append(current_item)
            i += 1
    
    # --- 그룹화 로직 종료 ---

    return grouped_analysis_data

# 그룹화된 데이터를 기반으로 하이라이트를 적용합니다.
def apply_highlights_to_page(page, analysis_data, translated_data, existing_highlight_rects, highlight_map):
    for ing, kor in zip(analysis_data, translated_data):
        ing_key = list(ing.keys())[0]
        ing_value = list(ing.values())[0]
        kor_value = list(kor.values())[0]

        if not ing_value or ing_value == "None":
            continue
        
        if ing_value in highlight_map:
            details = highlight_map[ing_value]
            description_text = details["desc_key"] + kor_value

            try:
                text_instances = page.search_for(ing_key.strip(), flags=fitz.TEXT_PRESERVE_WHITESPACE)

                if not text_instances:
                    print(f"    ⚠️ 경고: '{ing_key}' 텍스트를 페이지에서 찾지 못했습니다.")
                    continue

                for inst in text_instances:
                    is_already_highlighted = any(inst.intersects(rect) for rect in existing_highlight_rects)
                    if is_already_highlighted:
                        print(f"    ⏭️ 건너뛰기: '{ing_key}' 영역이 이미 다른 요소로 하이라이트 처리되었습니다.")
                        continue

                    highlight = page.add_highlight_annot(inst)
                    highlight.set_colors(stroke=details["color"])
                    highlight.set_info(info={"content": description_text})
                    highlight.update()
                    existing_highlight_rects.append(inst)
                    print(f"    ✅ '{ing_key}' ({ing_value}) 하이라이트 완료.")
                    break

            except Exception as e:
                print(f"    ❌ '{ing_key}' 하이라이트 중 오류 발생: {e}")
        else:
            pass
