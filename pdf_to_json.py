import os
import fitz
import json
import re
from langchain_community.llms import Ollama

#设置pdf的路径，以及json文件夹路径
PDF_DIR = "./datasheet"
JSON_DIR = "./json"

#如果json文件夹不存在 就创建
os.makedirs(JSON_DIR, exist_ok=True)

llm = Ollama(model="llama3", temperature=0)

# ------------------PDF to json use ollama----------------
def extract_specification_from_pdf(pdf_path):

    #打开PDF并提取全文
    doc = fitz.open(pdf_path)
    full_text = "\n".join([page.get_text() for page in doc])
    doc.close()

    full_text = (
        full_text
        .replace("•", "-")
        .replace("\no ", "\n- ")
    )

    cleaned_text = normalize_spec_text(full_text)

    #用ollama提取Specification
    prompt = f"""

You are an AI agent specialized in extracting IoT device specifications from datasheets.

INSTRUCTIONS:
1. Focus ONLY on the section titled "Specification", "Specifications", or "Technical Specifications".
2. Extract every key-value pair exactly as written.
   - Treat any line with a colon ":" as key-value.
   - If a line does not have a colon, put it in a "notes" list.
3. Output ONLY valid JSON with two keys: 
   - "Specification": a dictionary of all key-value pairs.
   - "notes": a list of any additional lines.
4. DO NOT add explanations, extra text, greetings, or markdown code blocks.
5. If you are unsure about a field, include it in "notes" instead of omitting it.
6. Make sure to capture all information in the "Specification" section, do not skip anything.
7. Ignore all other sections like "Features", "Applications", or "Electrical Characteristics".



Document text:
{cleaned_text}
"""
    #调用ollama
    #print(prompt)
    json_output = llm.invoke(prompt)

    spec_dict = parse_llm_json_output(json_output)

    return spec_dict


def parse_llm_json_output(llm_output):
    # 用正则提取 JSON 块
    match = re.search(r"\{.*\}", llm_output, re.DOTALL)
    if match:
        json_str = match.group()
        try:
            return json.loads(json_str)
        except:
            pass
    # 解析失败就放到 notes
    return {"Specification": {}, "notes": [llm_output]}

def normalize_spec_text(text: str) -> str:
    lines = []
    buffer = ""

    for line in text.splitlines():
        line = line.strip()

        if line == "-":
            continue

        if ":" in line:
            lines.append(line)
        else:
            lines.append(line)

    return "\n".join(lines)


#-------------------处理单个---------------------------------
# device_name = "SEN0203"
# pdf_path = os.path.join(PDF_DIR, device_name + ".pdf")
# json_path = os.path.join(JSON_DIR, device_name + ".json")

# print(f"Processing {device_name}...")

# spec_dict = extract_specification_from_pdf(pdf_path)

# # 保存 JSON
# with open(json_path, "w", encoding="utf-8") as f:
#     json.dump(spec_dict, f, indent=4, ensure_ascii=False)

# print(f"Saved {json_path}")
# print("Done!")






#--------------批量处理PDF--------------
for filename in os.listdir(PDF_DIR):
    if not filename.lower().endswith(".pdf"):
        continue

    pdf_path = os.path.join(PDF_DIR, filename)
    device_name = os.path.splitext(filename)[0]
    print(f"Processing {device_name}...")
    #生成JSON文件路径
    json_path = os.path.join(JSON_DIR, device_name + ".json")
    #已存在就跳过
    if os.path.exists(json_path):
        print(f"{json_path} already exists, skipping.")
        continue

    spec_dict = extract_specification_from_pdf(pdf_path)

    #保存JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(spec_dict, f, indent=4, ensure_ascii=False)

    print(f"Saved {json_path}")







#---------------处理单个-----------------
# You are a STRICT IoT specification extractor.

# TASK:
# 1. Locate the section that starts with the exact line "Specification".
# 2. Extract ALL lines after "Specification" that contain ":" or "：" as key-value pairs.
# 3. Stop extraction when you reach a blank line or another section (like Applications, Board Overview, etc.).
# 4. Lines without ":" should go into a list called "notes".
# 5. Output ONLY valid JSON in this format:

# {{
#     "Specification": {{ ...key-value pairs... }},
#     "notes": [ ...other lines... ]
# }}

# Do NOT summarize, infer, or skip any line.