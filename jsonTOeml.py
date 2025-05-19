import json
import os
import re

def sanitize_filename(filename):
    """
    Removes or replaces characters that are invalid in filenames.
    Args:
        filename (str): The proposed filename.
    Returns:
        str: A sanitized filename.
    """
    if not filename:
        return ""
    # Remove characters that are invalid in most file systems
    # and replace others (like spaces) with underscores.
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    filename = re.sub(r'\s+', '_', filename)
    # Limit length to avoid issues with long filenames
    return filename[:200]

def convert_json_to_eml(json_file_path, output_dir):
    """
    Converts email objects from a JSON file into individual .eml files.

    Args:
        json_file_path (str): Path to the input JSON file.
        output_dir (str): Directory where .eml files will be saved.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            emails_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file not found at '{json_file_path}'")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{json_file_path}'. Make sure it's a valid JSON file.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading the JSON file: {e}")
        return

    if not isinstance(emails_data, list):
        print("Error: JSON file should contain a list of email objects.")
        return

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Created output directory: '{output_dir}'")
        except OSError as e:
            print(f"Error creating output directory '{output_dir}': {e}")
            return

    print(f"Found {len(emails_data)} emails in '{json_file_path}'. Starting conversion...")

    for i, email_obj in enumerate(emails_data):
        if not isinstance(email_obj, dict):
            print(f"Warning: Skipping item at index {i} as it's not a dictionary (email object).")
            continue

        headers = email_obj.get('headers', {})
        body = email_obj.get('body', '')

        if not isinstance(headers, dict):
            print(f"Warning: Headers for email at index {i} are not in the expected dictionary format. Skipping.")
            continue

        eml_content = ""
        # Construct headers part
        for key, value in headers.items():
            # Ensure multi-line headers are correctly formatted
            # (though the previous script should handle this during parsing)
            if isinstance(value, str):
                eml_content += f"{key}: {value}\n"
            elif isinstance(value, list): # Should not happen with the provided JSON structure
                for v_line in value:
                    eml_content += f"{key}: {v_line}\n"


        # Add a blank line between headers and body
        eml_content += "\n"
        
        # Add body
        eml_content += body if isinstance(body, str) else str(body) # Ensure body is a string

        # Determine filename
        filename_base = ""
        if 'X-CCC-HASH' in headers and headers['X-CCC-HASH']:
            filename_base = headers['X-CCC-HASH']
        elif 'Subject' in headers and headers['Subject']:
            filename_base = sanitize_filename(headers['Subject'])
        
        if not filename_base: # Fallback if hash and subject are missing/empty
            filename_base = f"email_{i + 1}"
        
        eml_filename = f"{filename_base}.eml"
        eml_file_path = os.path.join(output_dir, eml_filename)

        try:
            with open(eml_file_path, 'w', encoding='utf-8') as eml_file:
                eml_file.write(eml_content)
            print(f"Successfully created '{eml_file_path}'")
        except IOError as e:
            print(f"Error writing .eml file '{eml_file_path}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred while writing '{eml_file_path}': {e}")

    print(f"\nConversion complete. {len(emails_data)} .eml files generated in '{output_dir}'.")

# --- Main Execution ---
if __name__ == "__main__":
    # Define the input JSON file and the output directory for .eml files
    # You can change these to your actual file paths
    INPUT_JSON_FILE = "emails_filtered.json"  # Or "emails.json" if you want to use the original
    OUTPUT_EML_DIR = "eml_files"

    if not os.path.exists(INPUT_JSON_FILE):
        print(f"Error: Input JSON file '{INPUT_JSON_FILE}' not found in the current directory.")
        print("Please make sure the file exists or provide the correct path.")
    else:
        convert_json_to_eml(INPUT_JSON_FILE, OUTPUT_EML_DIR)
