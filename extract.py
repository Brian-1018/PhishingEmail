import re
import json
import os

def parse_mbox(mbox_content):
    """
    Parses content in Berkeley Mailbox (mbox) format.

    Args:
        mbox_content: A string containing the entire mbox file content.

    Returns:
        A list of dictionaries, where each dictionary represents an email
        with 'headers' (as a dictionary) and 'body' (as a string).
        Returns an empty list if no emails are found or in case of errors.
    """
    emails = []
    # Split emails based on the "From " line delimiter at the beginning of a line
    # Using regex with positive lookahead to keep the delimiter
    email_parts = re.split(r'(?=^From )', mbox_content, flags=re.MULTILINE)

    # The first split part might be empty if the file starts directly with "From "
    if email_parts and not email_parts[0].strip():
        email_parts.pop(0)

    if not email_parts:
        print("No emails found in the provided content.")
        return emails

    for email_text in email_parts:
        if not email_text.strip():
            continue # Skip empty parts if any

        email_data = {'headers': {}, 'body': ''}
        lines = email_text.splitlines() # Split into lines

        # Ensure there are lines to process
        if not lines:
            continue

        # The first line is the "From " envelope line, often skipped or handled separately.
        # We can store it if needed, or just start processing headers from the next line.
        # email_data['envelope_from'] = lines[0] # Optional: store the envelope line

        header_section = True
        header_lines = []
        body_lines = []

        # Iterate through lines starting from the second line (index 1)
        for i in range(1, len(lines)):
            line = lines[i]
            # Check for the blank line separating headers and body
            if header_section and not line.strip():
                header_section = False
                continue # Skip the blank line itself

            if header_section:
                header_lines.append(line)
            else:
                # Handle "> From " escaping in the body if necessary for reconstruction.
                # For simple extraction, we just add the line.
                # if line.startswith('> From '):
                #     body_lines.append(line[2:]) # Remove the '> ' prefix
                # else:
                body_lines.append(line)

        # Parse headers
        current_header_key = None
        for header_line in header_lines:
            # Check if it's a continuation line (starts with whitespace)
            if header_line and (header_line.startswith(' ') or header_line.startswith('\t')):
                if current_header_key and current_header_key in email_data['headers']:
                     # Append continuation line to the last header value
                     email_data['headers'][current_header_key] += '\n' + header_line.strip()
                # else: handle malformed continuation line if needed
            else:
                # It's a new header line
                match = re.match(r'^([\w-]+):\s*(.*)', header_line)
                if match:
                    key, value = match.groups()
                    # Store header, handle potential duplicate headers by appending
                    # or decide on a different strategy (e.g., keep first/last)
                    # For simplicity, let's overwrite or keep the first occurrence.
                    # A common approach is to store multiple values in a list,
                    # but for this example, we'll keep it simple.
                    if key not in email_data['headers']:
                         email_data['headers'][key] = value.strip()
                         current_header_key = key # Track the current header for continuations
                    # else: handle duplicate headers if needed

        # Join body lines
        email_data['body'] = '\n'.join(body_lines)
        emails.append(email_data)

    return emails

def extract_emails_to_json(input_filename="year2005.txt", output_filename="emails.json"):
    """
    Reads an mbox file, parses emails, and exports them to a JSON file.

    Args:
        input_filename (str): The name of the input mbox file.
        output_filename (str): The name of the output JSON file.
    """
    try:
        # Check if the input file exists
        if not os.path.exists(input_filename):
            print(f"Error: Input file '{input_filename}' not found.")
            print(f"Current directory: {os.getcwd()}")
            print(f"Files in current directory: {os.listdir('.')}")
            return

        # Read the mbox file content
        with open(input_filename, 'r', encoding='utf-8', errors='ignore') as f:
            mbox_content = f.read()

        # Parse the emails
        emails_data = parse_mbox(mbox_content)

        if not emails_data:
            print("No emails were parsed.")
            return

        # Export the data to a JSON file
        with open(output_filename, 'w', encoding='utf-8') as json_file:
            json.dump(emails_data, json_file, indent=4, ensure_ascii=False)

        print(f"Successfully extracted {len(emails_data)} emails to '{output_filename}'")

    except FileNotFoundError:
        # This is another check, although os.path.exists should catch it first.
        print(f"Error: Input file '{input_filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- Main Execution ---
if __name__ == "__main__":
    # Define the input and output filenames
    INPUT_MBOX_FILE = "year2005.txt"
    OUTPUT_JSON_FILE = "emails.json"

    # Run the extraction process
    extract_emails_to_json(INPUT_MBOX_FILE, OUTPUT_JSON_FILE)
