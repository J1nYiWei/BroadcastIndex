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

    def timecode_to_seconds(timecode):
        """ Convert hh:mm:ss or h.mm.ss format to seconds """
        parts = timecode.replace(".", ":").split(":")
        parts = [int(p) for p in parts]
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
        return 0  # Fallback if format is unexpected

    for root, _, files in os.walk(ONEDRIVE_PATH):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                file_name = os.path.splitext(file)[0]  # Remove .txt extension
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                        if not lines:
                            continue  # Skip empty files

                        video_link = lines[0].strip()  # First line contains the video URL
                        matches_found = []
                        last_timecode = None

                        for line in lines[1:]:  # Skip first line (video link)
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
                                timecode_link = last_timecode
                                if last_timecode and video_link.startswith("http"):
                                    seconds = timecode_to_seconds(last_timecode)
                                    timecode_link = f'<a href="{video_link}?start={seconds}" target="_blank">{last_timecode}</a>'

                                # Add filename before the timestamp
                                matches_found.append({
                                    "timecode": f"<strong>{file_name}</strong> - {timecode_link}" if timecode_link else f"<strong>{file_name}</strong> - {last_timecode}",
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
