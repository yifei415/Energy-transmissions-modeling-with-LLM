import json
import os
from langchain_community.llms import Ollama

llm = Ollama(model="llama3", temperature=0)

PLAN_FILE = "plan_devices.json"
DATAJSON_DIR = "json"

# ================== 默认吞吐量 ==================
DEFAULT_THROUGHPUT = {
    "Wi-Fi": 100000,
    "BLE": 2000,
    "ZigBee": 250,
    "Thread": 250
}

# =============== 先裁剪执行计划吧 ==============

def extract_step_results(plan_json):
    """
    从执行计划 JSON 中提取 step_results

    plan_json: dict, 完整的执行计划 JSON
    :return: list,step_results
    """
    executions = plan_json.get("executions", [])
    if not executions:
        return []

    return executions[0].get("step_results", [])





# ================== 执行计划解析 ==================
def parse_execution_plan(plan_text):
    """
    调用LLM, 将执行计划解析成设备和模块
    """
    prompt = f"""
You are an AI assistant.
Given the following execution plan, extract all device IDs and the service being requested,
and also the time duration_ms.

Output ONLY a JSON array like:
[
  {{"device_id": "esp32-003", "modules": ["Camera"], "duration_ms": ["..."]}}
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

# ================== 保存 plan_devices.json ==================
def save_plan_devices(devices, output_path=PLAN_FILE):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(devices, f, indent=4, ensure_ascii=False)
    print(f"Saved devices and modules to {output_path}")

# ================== 读取相关设备 datasheet ==================
def load_relevant_device_specs():
    """
    根据 plan_devices.json 读取涉及设备的 datasheet
    """
    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        plan_devices = json.load(f)

    devices_specs = {}
    for entry in plan_devices:
        device_id = entry["device_id"]
        device_file = os.path.join(DATAJSON_DIR, f"{device_id}.json")
        if not os.path.exists(device_file):
            print(f"Missing datasheet for {device_id}")
            continue
        with open(device_file, "r", encoding="utf-8") as f:
            devices_specs[device_id] = json.load(f)

    return plan_devices, devices_specs

# ================== 用户选择协议 ==================
def choose_protocols(plan_devices):
    """
    交互式选择每个模块的通信协议
    """
    for device in plan_devices:
        device_id = device["device_id"]
        modules = device.get("modules", [])
        device["protocols"] = {}
        for module in modules:
            while True:
                protocol = input(
                    f"Select protocol for {device_id} - {module} "
                    "(Wi-Fi/BLE/ZigBee/Thread) [default Wi-Fi]: "
                ).strip()
                if protocol == "":
                    protocol = "Wi-Fi"
                if protocol in DEFAULT_THROUGHPUT:
                    device["protocols"][module] = protocol
                    break
                print("Invalid protocol. Choose from Wi-Fi, BLE, ZigBee, Thread.")
    return plan_devices


def extract_json_from_llm_output(llm_output: str):
    try:
        json_start = llm_output.find("{")
        json_end = llm_output.rfind("}") + 1
        json_str = llm_output[json_start:json_end]
        return json.loads(json_str)
    except Exception as e:
        raise ValueError("Cannot extract JSON from LLM output") from e


# ================== LLM 能耗 & 传输计算 ==================
def ask_llm_energy_transmission_with_trace(plan_devices, device_specs):
    """
    Ask LLM to compute energy and transmission for each module,
    show reasoning steps.
    """
    prompt = f"""
You are an Energy & Transmission Modeling Agent for an IoT deployment.

Execution plan devices (with chosen protocols):
{json.dumps(plan_devices, indent=2)}

Device datasheets (JSON):
{json.dumps(device_specs, indent=2)}

Rules:

First, provide step-by-step calculations in plain text for human inspection.

Then, provide the final result in STRICT JSON format.

1. If a field like "Supply Voltage" has a range (e.g., "3.3V to 5V"), use the first number (3.3) for calculations.
2. If a field like "Operating Current" has a valeur, use this valeur like Current, if not exist,the  Current: fixed 10 mA.
3. Assume Data_kb = 50 kb
4. Power (mW) = Supply Voltage (V) * Current (mA)
5. If in plan_devices has a duration_ms, use the for calculate Energy like time.
5. Energy (mJ) = Power (mW) * time (ms)
6. Transmission time (s) = Data_kb * 8 / Throughput_kbps
   (use throughput according to the chosen protocol for each module)



Task:
1. For each device and module, compute:
   - first explain step-by-step how you computed these values
   - Energy (mJ)
   - estimated_transmission_s

2. Determine overall:
   - energy_feasible
   - transmission_feasible

In the final JSON, also include:
- total_energy_mJ: sum of all energy_mJ values
- max_transmission_s: maximum of all estimated_transmission_s values
Do not explain how they are calculated.
   

JSON schema:
{{
  "summary": {{
    "total_energy_mJ": number,
    "max_transmission_s": number
  }},
  "calculation_steps": [
    {{
      "device_id": string,
      "module": string,
      "energy_mJ": number,
      "estimated_transmission_s": number
    }}
  ]
}}
"""
    return llm.invoke(prompt).strip()

# ================== 主流程 ==================
if __name__ == "__main__":
    # Step 1: 用户输入执行计划
    # 别急 先测试直接读执行计划
    # print("Enter your execution plan description (end with a blank line):")
    # lines = []
    # while True:
    #     line = input()
    #     if line.strip() == "":
    #         break
    #     lines.append(line)
    # plan_text = "\n".join(lines)

    # 测试1
    with open("execution_history.json", "r", encoding="utf-8") as f:
        plan_json = json.load(f)

    #print("先直接读执行计划")
    plan_text = extract_step_results(plan_json)

    #print(plan_text)

    # Step 2: 解析设备和模块
    devices = parse_execution_plan(plan_text)
    print("\nExtracted devices and modules by LLM:")
    print(json.dumps(devices, indent=4))

    # Step 3: 保存 plan_devices.json
    save_plan_devices(devices)

    # Step 4: 用户交互选择通信协议
    devices = choose_protocols(devices)
    save_plan_devices(devices)  # 更新协议信息到JSON

    # Step 5: 读取 datasheets
    plan_devices, device_specs = load_relevant_device_specs()

    # Step 6: LLM 计算能耗 & 传输
    result = ask_llm_energy_transmission_with_trace(plan_devices, device_specs)
    print("\n===== ENERGY & TRANSMISSION ANALYSIS =====")
    print(result)
    result_final = extract_json_from_llm_output(result)

    with open("result_final.json", "w", encoding="utf-8") as f:
        json.dump(result_final, f, indent=4)

    print("JSON saved successfully!")
