# IoT Project - LLM Assisted

This repository contains scripts to extract IoT device specifications from PDFs, process execution plans, and validate energy and transmission models using an LLM.

## Scripts Overview

### 1. `projet_iot.py`
- Extracts specifications from PDFs in the `datasheet` folder.
- Saves all specifications into `specifications.json`.
- Provides an interactive interface for energy and transmission model calculations using an LLM.

### 2. `pdf_to_json.py`
- Batch-processes PDFs in the `datasheet` folder.
- Extracts the "Specification" section from each PDF using Ollama.
- Saves each device’s structured data as a separate JSON file in the `json` folder.

### 3. `llm_read_execution_plan.py`
- Parses an execution plan using Ollama.
- Extracts device IDs and requested modules.
- Saves the structured result as `plan_devices.json`.

### 4. `llm_calculer_modele.py`
- Loads device data from `plan_devices.json` and the corresponding datasheet JSON files.
- Feeds the data to Ollama to “understand” the devices.
- Validates the execution plan’s energy and transmission feasibility.
- Outputs the validation results as JSON.

## Folder Structure

