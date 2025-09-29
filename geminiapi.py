import json

def analyze_sentence_with_gemini(sentence, page_no, client):
    """Gemini API를 사용하여 문장 성분을 분석하고 결과를 JSON으로 반환합니다."""
    prompt = f"""
Please analyze the ingredients and answer only with the JSON-type string below.
{{
    "pageNo": {page_no},
    "subject": "text", "subject_desc": "text",
    "verb": "text", "verb_desc": "text",
    "objective": "text", "objective_desc": "text",
    "complement": null, "complement_desc": null,
    "noun": null, "noun_desc": null,
    "adjective": null, "adjective_desc": null,
    "adverb": "text", "adverb_desc": "text",
    "article": null, "article_desc": null,
    "determiner": null, "determiner_desc": null,
    "preposition": "text", "preposition_desc": "text",
    "conjunction": null, "conjunction_desc": null,
    "interrogative": null, "interrogative_desc": null,
    "relative_pronoun": null, "relative_pronoun_desc": null,
    "modal": null, "modal_desc": null,
    "auxiliary": null, "auxiliary_desc": null,
    "gerund": null, "gerund_desc": null,
    "participle": null, "participle_desc": null,
    "infinitive": null, "infinitive_desc": null,
    "prepositional_phrase": null, "prepositional_phrase_desc": null,
    "clause": null, "clause_desc": null,
    "phrase": null, "phrase_desc": null,
    "modifier": null, "modifier_desc": null
}}

Every word must have one component.
In the JSON value, _desc, put the Korean interpretation of the ingredient.
If there is no corresponding ingredient, please make the corresponding value null.

Sentence: "{sentence}"
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        json_text = response.text.strip()
        if json_text.startswith("```json"):
            json_text = json_text[7:-3].strip()
            
        return json.loads(json_text)
    except json.JSONDecodeError:
        print(f"❌ Gemini가 반환한 값을 JSON으로 파싱하는 데 실패했습니다: {response.text}")
        return None
    except Exception as e:
        print(f"❌ Gemini API 호출 중 오류 발생: {e}")
        return None