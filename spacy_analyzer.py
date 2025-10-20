import spacy
import json

nlp = spacy.load("en_core_web_sm")  

# 명사-동사-형용사-접속사-전치사-부사-한정사-기타 : 빨주노초파남보 하늘 
ingredients = {
    "CC": "등위 접속사", # 초록
    "CD": "숫자", # 기타
    "DT": "한정사", # 보라
    "EX": "존재 표현", # 기타
    "FW": "외래어", # 기타
    "IN": "전치사/종속접속사", # 파랑
    "JJ": "형용사(원급)", # 노랑
    "JJR": "형용사(비교급)", # 노랑
    "JJS": "형용사(최상급)", # 노랑
    "LS": "나열 목록", # 기타
    "MD": "조동사", # 주황
    "NN": "단수명사", # 빨강
    "NNS": "복수명사", # 빨강
    "NNP": "단수 고유명사", # 빨강
    "NNPS": "복수 고유명사", # 빨강
    "PDT": "전치한정사", # 보라
    "POS": "소유격", # 기타
    "PRP": "인칭대명사", # 빨강
    "PRP$": "소유대명사", # 빨강
    "RB": "부사(원급)", # 남색
    "RBR": "부사(비교급)", # 남색
    "RBS": "부사(최상급)", # 남색
    "RP": "조사", # 파랑
    "TO": "to부정사", # 주황
    "UH": "감탄사", # 기타
    "VB": "동사", # 주황
    "VBG": "동명사", # 주황
    "VBD": "동사(과거완료)", # 주황
    "VBN": "과거분사", # 주황
    "VBP": "동사(3인칭 단수가 아닌 현재시제)", # 주황
    "VBZ": "동사(3인칭 단수인 현재시제)", # 주황
    "WDT": "의문명사", # 빨강
    "WP": "의문대명사", # 빨강
    "WRB": "의문부사" # 남색
}

# 문장 성분을 단어별로 분석하여 한국어 태깅으로 변경해 반환하는 함수
def analysis_sentence_ingredients(sentence):
    doc = nlp(sentence)
    tag = [(token.text, token.tag_) for token in doc]

    # 중복 단어도 순서대로 담기 위해 리스트 사용
    ingre_list = []
    for word, pos_tag in tag:
        if word != pos_tag:
            ingre_list.append({word: pos_tag})
        else:
            ingre_list.append({word: "None"})

    return ingre_list
