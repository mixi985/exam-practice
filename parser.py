# -*- coding: utf-8 -*-
"""手机版 - 题目文本解析器"""
import re
import json


def parse_text_block(text: str):
    """
    解析纯文本题库
    支持格式：
    1. 题目文本 ... 
       A. ...
       B. ...
       答案：A
       解析：...
    """
    if not text:
        return []
    questions = []
    # 按"题目"或数字编号分割
    blocks = re.split(r"\n\s*(?:\d+[.．、])", text)
    for i, block in enumerate(blocks):
        if not block.strip():
            continue
        q = parse_single_block(block.strip())
        if q and q.get("content"):
            questions.append(q)
    return questions


def parse_single_block(block: str):
    """解析单个题目块"""
    q = {"question_type": "single", "options": {}, "answer": "",
         "explanation": "", "content": ""}
    lines = [l.strip() for l in block.split("\n") if l.strip()]
    content_lines = []
    option_pattern = re.compile(r"^([A-Za-z])[.．、]\s*(.+)")
    ans_pattern = re.compile(r"^(?:答案|正确答案)[：: ]*(.+)")
    exp_pattern = re.compile(r"^(?:解析|解释|说明)[：: ]*(.+)")

    for line in lines:
        m = option_pattern.match(line)
        if m:
            key = m.group(1).upper()
            q["options"][key] = m.group(2).strip()
            continue
        m = ans_pattern.match(line)
        if m:
            q["answer"] = m.group(1).strip().upper().replace(" ", "")
            # 判断题
            if q["answer"] in ("对", "TRUE", "√", "T"):
                q["answer"] = "对"
                q["question_type"] = "judgment"
            elif q["answer"] in ("错", "FALSE", "×", "F"):
                q["answer"] = "错"
                q["question_type"] = "judgment"
            elif len(q["answer"]) > 1:
                q["question_type"] = "multiple"
            continue
        m = exp_pattern.match(line)
        if m:
            q["explanation"] = m.group(1).strip()
            continue
        content_lines.append(line)
    q["content"] = " ".join(content_lines)
    # 判断题补全选项
    if q["question_type"] == "judgment":
        q["options"] = {"对": "正确", "错": "错误"}
    return q


def parse_docx(filepath: str):
    """解析 docx 文件（在 Android 上若缺少 docx 库则回退到文本模式）"""
    try:
        from docx import Document
        doc = Document(filepath)
        text = "\n".join([p.text for p in doc.paragraphs])
        return parse_text_block(text)
    except Exception:
        # 回退：按 txt 模式读取
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            return parse_text_block(text)
        except Exception:
            return []
