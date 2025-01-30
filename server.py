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
    timecode_pattern = re.compile(r"\b\d{1,2}[:.]\d{2}[:.]\d{2}\b")  # Matches timecodes like 1.34.00 or 0:17:00

    for root, _, files in os.walk(ONEDRIVE_PATH):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                        if not lines:
                            continue  # Skip empty files

                        video_link = lines[0].strip()  # First line contains the video URL
                        matches_found = []
                        last_timecode = None

                        for line in lines[1:]:  # Skip the first line (video link)
                            # Check if the line contains a timecode
                            timecode_match = timecode_pattern.search(line)
                            if timecode_match:
                                last_timecode = timecode_match.group(0)

                            # Check if the line contains the query
                            if re.search(re.escape(query), line, re.IGNORECASE):
                                # Highlight the query in the line
                                highlighted_line = re.sub(
                                    re.escape(query),
                                    f"<mark>{query}</mark>",
                                    line,
                                    flags=re.IGNORECASE
                                )

                                # Convert timecode to a clickable URL
                                timecode_link = ""
                                if last_timecode and video_link.startswith("http"):
                                    # Convert timecode to YouTube-style timestamp (hh:mm:ss)
                                    timestamp = last_timecode.replace(".", ":")
                                    timecode_link = f'<a href="{video_link}?t={timestamp}" target="_blank">{last_timecode}</a>'

                                matches_found.append({
                                    "timecode": timecode_link or last_timecode,  # Use link if available
                                    "text": highlighted_line.strip()
                                })

                        if matches_found:
                            results.append({
                                "file": file,
                                "video_url": video_link,
                                "matches": matches_found
                            })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    return jsonify(results)






if __name__ == '__main__':
    app.run(debug=True)
