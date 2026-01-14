import json
import os
from langchain_community.llms import Ollama

llm = Ollama(model="llama3", temperature=0)


def parse_execution_plan(plan_text):

    #调用LLM, 将执行计划解析成设备

    prompt = f"""
You are an AI assistant.
Given the following execution plan, extract all device IDs and the modules being requested.
Output ONLY a JSON array like:
[
  {{"device_id": "esp32-003", "modules": ["Camera"]}}
]
Do NOT include any extra text, explanation, or markdown formatting.

Execution Plan:
{plan_text}

"""
    
    llm_output = llm.invoke(prompt).strip()
    
    try:
        device_modules = json.loads(llm_output)
    except json.JSONDecodeError:
        print("LLM output is not valid JSON. Raw output:")
        print(llm_output)
        device_modules = []

    return device_modules

#---------储存设备名和模块解析结果为json文件------------

def save_plan_devices(devices, output_path="plan_devices.json"):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(devices, f, indent=4, ensure_ascii=False)
    print(f"Saved devices and modules to {output_path}")





if __name__ == "__main__":

    plan_text = """
devices:
    - DFR0034
        -camera
"""
    devices = parse_execution_plan(plan_text)
    print("Extracted devices and modules:")
    print(json.dumps(devices, indent=4))

    #保存
    save_plan_devices(devices)