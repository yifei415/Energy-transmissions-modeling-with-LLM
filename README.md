projet_iot.py : this script extracts specifications from PDFs in the datasheet folder, saves them as specifications.json, and allows interactive energy and transmission model calculations using an LLM.

pdf_to_json.py : this script batch-processes PDFs in the datasheet folder, extracts the "Specification" section from each using Ollama, and saves each device’s structured data as a JSON file in the json folder.

llm_read_excution_plan.py : this script uses Ollama to parse an execution plan, extracting device IDs and their requested modules, and saves the structured result as plan_devices.json.

llm_calculer_modele.py : This script loads device data from `plan_devices.json` and the corresponding datasheet JSON files, feeds them to Ollama to internally understand the devices, and then uses the LLM to validate the execution plan’s energy and transmission feasibility, outputting the results as JSON.
