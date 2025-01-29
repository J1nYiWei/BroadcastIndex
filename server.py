from flask import Flask, request, jsonify, send_from_directory
import os
import re

app = Flask(__name__)

# Set the path to the 'files' directory
ONEDRIVE_PATH = os.path.join(os.path.dirname(__file__), 'files')

@app.route('/')
def home():
    # Serve the index.html file
    return send_from_directory('.', 'index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    results = []

    for root, _, files in os.walk(ONEDRIVE_PATH):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.readlines()  # Read the file line by line

                        matches_found = []

                        for line in content:
                            if re.search(re.escape(query), line, re.IGNORECASE):
                                # Highlight the query in the line
                                highlighted_line = re.sub(
                                    re.escape(query),
                                    f"<mark>{query}</mark>",
                                    line,
                                    flags=re.IGNORECASE
                                )
                                matches_found.append(highlighted_line.strip())

                        if matches_found:
                            results.append({
                                "file": file,
                                "matches": matches_found
                            })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    return jsonify(results)




if __name__ == '__main__':
    app.run(debug=True)
