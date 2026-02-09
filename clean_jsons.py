import json
import os

def clean_json(data, filename):
    if isinstance(data, dict):
        # Global removals
        data.pop('metadata', None)
        data.pop('scraped_at', None)
        
        # File-specific removals
        if "workshops" in filename:
            data.pop('slug', None)
        if "speakers" in filename:
            data.pop('image_url', None)
            
        # Recursively clean nested dictionaries or lists
        for key in list(data.keys()):
            data[key] = clean_json(data[key], filename)
    elif isinstance(data, list):
        # Recursively clean each item in the list
        data = [clean_json(item, filename) for item in data]
    return data

def process_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            print(f"Processing {filepath}...")
            with open(filepath, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error decoding {filename}")
                    continue
            
            cleaned_data = clean_json(data, filename)
            
            with open(filepath, 'w') as f:
                json.dump(cleaned_data, f, indent=2)
            print(f"Finished processing {filepath}")

if __name__ == "__main__":
    target_dir = "/home/hamzah/Desktop/dhs-2026-chatbot/jsons_2025"
    process_directory(target_dir)
