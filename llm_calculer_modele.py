import json
import os
from langchain_community.llms import Ollama

llm = Ollama(model="llama3", temperature=0)

PLAN_FILE = "plan_devices.json"
DATAJSON_DIR = "json"

def load_relevant_device_specs():
    #读取plan_devices.json
    #加在涉及到的设备的JSON
    #返回一个dict

    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        plan_devices = json.load(f)

    devices_specs = {}

    for entry in plan_devices:
        device_id = entry["device_id"]
        device_file = os.path.join(DATAJSON_DIR, f"{device_id}.json")

        if not os.path.exists(device_file):
            print(f"Missing data for {device_id}")
            continue

        with open(device_file, "r", encoding="utf-8") as f:
            devices_specs[device_id] = json.load(f)

    return plan_devices, devices_specs


def ask_llm_to_read_specs(plan_devices, device_specs):
    """
    把 plan + datasheet JSON 交给 LLM
    让它“读懂”，但暂时不做计算
    """

    prompt = f"""
You are an IoT Device Analysis Agent.

Execution plan devices:
{json.dumps(plan_devices, indent=2)}

Device datasheets (JSON):
{json.dumps(device_specs, indent=2)}

Acknowledge internally.
Do not output any data.
"""

    llm.invoke(prompt)

def ask_llm_energy_transmission_validation():
    """
    Ask the LLM to validate the execution plan
    in terms of energy and transmission constraints.
    """

    prompt = """
You are an Energy and Transmission Modeling Agent for an IoT deployment.

You have already been provided with:
- The execution plan devices
- The detailed datasheets of the involved devices

Task:
Evaluate whether the execution plan is VALID with respect to:
1. Energy consumption
2. Network transmission constraints

Consider:
- Number of active devices
- High-power sensors (e.g., cameras)
- Sampling frequency
- Data transmission volume

Output ONLY JSON in the following format:
{
  "energy_feasible": true | false,
  "transmission_feasible": true | false,
  "reasons": ["..."],
  "recommendations": ["..."]
}
"""

    response = llm.invoke(prompt).strip()
    return response










if __name__ == "__main__":
    # Step 1: inject execution plan + datasheets
    plan_devices, device_specs = load_relevant_device_specs()
    ask_llm_to_read_specs(plan_devices, device_specs)

    # Step 2: energy & transmission validation
    validation_output = ask_llm_energy_transmission_validation()

    print("\n===== ENERGY & TRANSMISSION VALIDATION =====")
    print(validation_output)
