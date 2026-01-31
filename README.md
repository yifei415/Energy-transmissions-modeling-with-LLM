# IoT Energy & Transmission Modeling Project

## 1. Documentation Harvesting

**Objective:** Collect and analyze datasheets for all components used in the IoT deployment.  

**Components collected:**

- **DFRobot 37-piece sensor kit**: Datasheets for all 37 sensors have been collected.  
- **Microcontrollers**: ESP32-C6 and ESP32-S3 datasheets have been included.  

**Location:** All datasheets are stored in the `datasheet/` folder in this repository.

**Purpose:** These datasheets provide essential parameters for energy consumption and network transmission modeling, including:  

- Supply voltage and operating currents  

---

**Next steps:** Extract the relevant parameters from these datasheets, convert them into structured JSON files, and store them for use in constructing accurate energy and transmission models for the IoT deployment.


## 2. Parameter Extraction and JSON Conversion

**Objective:** Convert datasheet specifications into structured data for modeling.

**Procedure:**

1. For each component datasheet (PDF), use **Ollama** to extract the **Specification** section.  
2. Store the extracted parameters in a **single JSON file per component**.  
   - Example: `datasheet/DFR0017.json`, `datasheet/0022.json`  
3. These JSON files will serve as the structured input for **energy and transmission modeling**.

**Purpose:** This approach standardizes the data and makes it easy to use programmatically for simulations and calculations.




## 3. Execution Plan Processing and Device Data Preparation

**Objective:** Transform raw execution plans into structured device-level data for modeling.

**Procedure:**
1. **Initial Execution Plan:** Stored in `execution_history.json` containing detailed logs.
2. **Extract Step Results:**  
   Extract `step_results` to keep only relevant fields:
3. **Simplify Execution Plan via Ollama:**  
   - Feed the extracted step results to **Ollama**.  
   - Ollama processes the data and returns a **simplified execution plan** containing only the essential fields:
   ```json
   {
        "device_id": "DFR0022",
        "modules": [
            "Camera"
        ],
        "duration_ms": 1200
    }
4. **Store Simplified Plan:**
    - Save the simplified execution plan to plan_devices.json.
    - This file now contains a clean list of devices and their modules with execution durations.
5. **Match Devices with Datasheets:**
    - For each device in plan_devices.json, identify the corresponding JSON file from the json/ folder.
    - Each JSON file contains component-specific parameters extracted in Step 2.
7. **Load Device Specifications:**
    - Create an empty Python dictionary to hold all device specifications.
    ```python
    devices_specs = {}
6. **Feed Data to LLM (Ollama):**
    - Provide the device parameters(devices_specs) to Ollama for further processing

## 4. Assign Communication Protocols

**Objective:** Assign a communication protocol to each device/module, since the execution plan does not include protocol information by default.

**Procedure:**

1. **Load Simplified Plan:**  
   - Read `plan_devices.json` containing the simplified execution plan with devices, modules, and durations.

2. **Select Protocols:**  
   - For each device/module, manually choose an appropriate communication protocol, for example:
     - Wi-Fi
     - BLE
     - ZigBee
     - Thread

3. **Update Plan Devices:**  
   - Add the chosen protocol to each device/module entry in `plan_devices.json`.  
   - Example:

    ```json
    {
        "device_id": "DFR0022",
        "modules": [
            "Camera"
        ],
        "duration_ms": 1200,
        "protocols": {
            "Camera": "Wi-Fi"
        }
    }

4. **Save Updated Plan**  


## 9. Energy and Transmission Calculation with Ollama

**Objective:** Compute energy consumption and estimated transmission time for each device/module using Ollama, and store the results in JSON format.

**Procedure:**

1. **Prepare Input for Ollama:**  
   - Combine simplified execution plan (`plan_devices.json`) with device specifications (`devices_specs` dictionary).  

2. **Invoke Ollama for Calculations:**  
   - Feed the prepared data to Ollama.  
   - Request Ollama to compute:
     - Energy consumption (mJ) for each module: `Energy = Power × Duration`  
     - Estimated transmission time (s) based on protocol and throughput

3. **Extract Ollama Output:**  
   - Capture Ollama's response.  
   - Parse the JSON-formatted result from the output (ignore extra text or step-by-step explanations if present).

4. **Store Final Results:**  
   - Save the extracted data as a JSON file (e.g., `result_final.json`) with structure:

    ```json
    {
        "summary": {
            "total_energy_mJ": 121.6,
            "max_transmission_s": 0.04
        },
        "calculation_steps": [
            {
                "device_id": "DFR0022",
                "module": "Camera",
                "energy_mJ": 39.6,
                "estimated_transmission_s": 0.04
            },
        ]
    }