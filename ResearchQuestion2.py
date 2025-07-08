# from mistralai.client import MistralClient

# api_key = "rijjAgLagi1h6KtADdLyFIOq2tPNbK8s"
# client = MistralClient(api_key=api_key)
from openai import OpenAI
import os 
import json
import re
client = OpenAI(
    base_url="https://api.mistral.ai/v1",
    api_key="rijjAgLagi1h6KtADdLyFIOq2tPNbK8s"
)

# Enhanced prompt tailored for social science methodologies
prompt = """
You are an expert research assistant specialized in analyzing social science academic papers which focus the use og Generative AI in Retail.

Given the following academic text, analyze it thoroughly and extract the following structured information. Read the full content and infer which methodologies are **central to the research design** (major) and which are **supporting or secondary** (minor). A study usually has **one or two major methodologies**, while others may be mentioned but play a lesser role.

Return your output in the following JSON structure:

{
  "Major_Theories": ["<List the primary social science theories explicitly mentioned or strongly implied>"],

  "Research_Methodologies": {
    "Major_Methodologies": ["<1–2 core methods used in the study>"],
    "Minor_Methodologies": ["<Other methods mentioned or used in a secondary role>"],
    "Sample": "<Summarize the sample, including quantifiable details such as number of subjects, interviews conducted, papers reviewed, or datasets analyzed>",
    "Design": "<Brief description of research design (e.g., qualitative, quantitative, mixed-methods)>"
  },

  "Dataset_Types": ["<Clearly specify types of data used, e.g., survey responses, interview transcripts, statistical data, archival records, etc.>"],

  "Disciplinary_Context": "<State the academic domain(s), such as sociology, anthropology, political science, communication studies>",

  "Keywords": ["<List 3–5 key concepts, terms, or techniques relevant to the paper>"]
}

Text:
"""

def extract_info_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        text_content = file.read() # Truncate if too long

    response = client.chat.completions.create(
        model="mistral-large-2407",
        messages=[
            {"role": "system", "content": "Extract structured data from academic text."},
            {"role": "user", "content": prompt + text_content}
        ],
        temperature=0.0,
        max_tokens=500
    )

    return response.choices[0].message.content

# Directory structure processing
root_dir = "/Users/akashdas/Desktop/IU MS DS FALL 2023/SEMESTER 4 - SPRING 2025/FADS 2025/Data/Data "
output_data = {}
output_txt_dir = "results/outputs"
os.makedirs(output_txt_dir, exist_ok=True)
c=0
for subdir, _, files in os.walk(root_dir):
    for file in files:
        if file.lower().endswith('.txt'):
            filepath = os.path.join(subdir, file)
            print(f"Processing: {filepath}")
            structured_response = extract_info_from_file(filepath)

            # Extract JSON from response
            json_match = re.search(r"\{.*\}", structured_response, re.DOTALL)

            key_name = os.path.splitext(file)[0]  # Remove .txt

            if json_match:
                json_str = json_match.group(0)
                try:
                    parsed_json = json.loads(json_str)
                    output_data[key_name] = parsed_json

                    # Save individual response to txt file
                    output_file_path = os.path.join(output_txt_dir, f"{key_name}_method.txt")
                    with open(output_file_path, "w", encoding="utf-8") as out_txt:
                        json.dump(parsed_json, out_txt, indent=4)
                    c+=1
                    print("Papers properly extracted: {}".format(c))
                except json.JSONDecodeError as e:
                    print(f"JSON decoding error for {file}: {e}")
                    output_data[key_name] = {"error": "Invalid JSON", "raw_response": structured_response}
            else:
                print(f"No JSON found in response for {file}")
                output_data[key_name] = {"error": "No JSON found", "raw_response": structured_response}

# Save all outputs to JSON file
with open("results/results2.json", "w", encoding="utf-8") as json_file:
    json.dump(output_data, json_file, indent=4)

print("✅ JSON extraction complete. Outputs saved to 'results.json'")