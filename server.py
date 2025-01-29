from flask import Flask, request, jsonify, send_from_directory
import os
import re

app = Flask(__name__)

# Set OneDrive folder path
ONEDRIVE_PATH = r"C:\Users\mysta\OneDrive\JW BroadcastIndex"

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')  # Serves index.html from the current directory

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        print("No query provided")
        return jsonify([])

    print(f"Received search query: '{query}'")
    results = []

    files_scanned = 0  # Track the number of files scanned
    for root, _, files in os.walk(ONEDRIVE_PATH):
        print(f"Checking directory: {root}")
        for file in files:
            if file.endswith(".txt"):
                files_scanned += 1
                file_path = os.path.join(root, file)
                print(f"Scanning file: {file_path}")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if query.lower() in content.lower():
                            print(f"Query '{query}' found in {file_path}")
                        else:
                            print(f"Query '{query}' NOT found in {file_path}")

                        # Same matching logic
                        matches = [m for m in re.finditer(re.escape(query), content, re.IGNORECASE)]
                        if matches:
                            occurrences = []
                            for match in matches:
                                start = max(match.start() - 50, 0)
                                end = min(match.end() + 50, len(content))
                                context = content[start:end].replace("\n", " ") + "..."
                                occurrences.append(f"...{context}...")

                            results.append({
                                "file": file,
                                "matches": occurrences
                            })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    print(f"Files scanned: {files_scanned}")  # Log the number of files scanned
    print(f"Search results: {results}")  # Log results
    return jsonify(results)




if __name__ == '__main__':
    app.run(debug=True)
