import os
import fitz  # PyMuPDF
from langchain_community.llms import Ollama
import json

# PDF 文件夹 & 输出 JSON
PDF_DIR = "datasheet"
OUTPUT_FILE = "specifications.json"

# 初始化 LLM
llm = Ollama(model="llama3", temperature=0)

# 协议参数示例（Task2使用）
protocols = {
    "Wi-Fi": {"range_m": 50, "latency_ms": 10, "throughput_kbps": 100000, "reliability": 0.98},
    "BLE": {"range_m": 30, "latency_ms": 10, "throughput_kbps": 2000, "reliability": 0.95},
    "ZigBee": {"range_m": 100, "latency_ms": 80, "throughput_kbps": 250, "reliability": 0.9},
    "Thread": {"range_m": 100, "latency_ms": 70, "throughput_kbps": 250, "reliability": 0.92},
}

# -------------------- Task1：Specification 提取 --------------------
def parse_specification_text(spec_text):
    spec_dict = {}
    notes = []
    lines = [line.strip("• ").strip() for line in spec_text.split("\n") if line.strip()]
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            spec_dict[key.strip()] = value.strip()
        else:
            notes.append(line)
    return spec_dict, notes

def extract_specification_from_pdf(pdf_path, device_name=None):
    doc = fitz.open(pdf_path)
    full_text = "\n".join([page.get_text() for page in doc])

    prompt = f"""
You are an AI agent for extracting the SPECIFICATION section from an IoT datasheet.

INSTRUCTIONS:
- Focus ONLY on the text under the "Specification", "Specifications", or "Technical Specifications" heading.
- Extract every line exactly as written.
- Do NOT generate JSON.
- Ignore any text outside the SPECIFICATION section.

Document content:
{full_text}
"""
    response = llm.invoke(prompt)
    return response  # 返回原始 SPECIFICATION 文本

# -------------------- Task2：能耗计算 --------------------
def compute_energy_model(spec, protocol):
    """
    简化能耗计算示例：
    E_tx = V * I_tx * t_tx
    E_rx = V * I_rx * t_rx
    总能耗 = E_tx + E_rx
    """
    # 从规格里读取电压和电流，缺失字段用默认值
    V = float(spec.get("Operating Voltage", spec.get("Voltage Range", "3.3").split()[0]))
    I_tx_mA = float(spec.get("TX Current", spec.get("Current Consumption", "20").split()[0]))
    I_rx_mA = float(spec.get("RX Current", spec.get("Current Consumption", "15").split()[0]))

    t_tx_ms = 10  # 假设每次发送10ms
    t_rx_ms = 10  # 假设每次接收10ms

    E_tx_mJ = V * (I_tx_mA / 1000) * t_tx_ms
    E_rx_mJ = V * (I_rx_mA / 1000) * t_rx_ms
    E_total_mJ = E_tx_mJ + E_rx_mJ

    return {
        "tx_energy_mJ": round(E_tx_mJ, 3),
        "rx_energy_mJ": round(E_rx_mJ, 3),
        "total_energy_mJ": round(E_total_mJ, 3)
    }

def get_transmission_model(protocol_name):
    return protocols.get(protocol_name, {})

# -------------------- 交互式 Agent --------------------
def interactive_agent(specs):
    print("\nInteractive IoT Specification + Energy/Transmission Agent")
    print("Type 'exit' at any time to quit.\n")

    while True:
        device_query = input("Enter device name: ").strip()
        if device_query.lower() == "exit":
            break

        device_spec = specs.get(device_query)
        if not device_spec:
            print(f"Device '{device_query}' not found.\n")
            continue

        # 显示原始 Specification
        user_question = input("Enter 'show' to see full SPECIFICATION or 'compute' for energy/tx model: ").strip()
        if user_question.lower() == "show":
            print(json.dumps(device_spec, indent=2, ensure_ascii=False))
            print("-" * 60)
            continue
        elif user_question.lower() == "compute":
            # 选择协议
            print("Available protocols:", ", ".join(protocols.keys()))
            protocol_choice = input("Select protocol: ").strip()
            if protocol_choice not in protocols:
                print("Invalid protocol.")
                continue

            # Task2计算
            spec_fields = device_spec["Specification"]
            energy = compute_energy_model(spec_fields, protocol_choice)
            transmission = get_transmission_model(protocol_choice)

            result = {
                "device": device_query,
                "protocol": protocol_choice,
                "energy_model": energy,
                "transmission_model": transmission
            }

            print("\nComputed Energy and Transmission Model:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("-" * 60)
            continue

        print("Invalid input. Type 'show' or 'compute'.")
        print("-" * 60)

# -------------------- 主函数 --------------------
def main():
    results = {}

    # 如果 JSON 已存在，直接读取
    if os.path.exists(OUTPUT_FILE):
        print(f"Found existing {OUTPUT_FILE}, loading...")
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            results = json.load(f)
    else:
        for file in os.listdir(PDF_DIR):
            if not file.lower().endswith(".pdf"):
                continue
            pdf_path = os.path.join(PDF_DIR, file)
            device_name = os.path.splitext(file)[0]
            print(f"Processing {file}...")

            try:
                spec_text = extract_specification_from_pdf(pdf_path, device_name=device_name)
                spec_dict, notes = parse_specification_text(spec_text)
                results[device_name] = {
                    "device": device_name,
                    "Specification": spec_dict,
                    "notes": notes
                }
            except Exception as e:
                print(f"Error processing {file}: {e}")

        # 保存 Task1 JSON
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nAll specifications extracted and saved to {OUTPUT_FILE}")

    # 交互式查询 + Task2 计算
    interactive_agent(results)

if __name__ == "__main__":
    main()
