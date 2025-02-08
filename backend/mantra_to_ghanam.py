from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from different origins (e.g. Next.js on http://localhost:3000)

# -- Transformation Logic (unchanged) --

def transform_word(word, overall_pos, seg_index, block_type, pos_in_block):
    """
    Transform the original word based on:
      - overall_pos: the word’s position in the full mantra (1-indexed)
      - seg_index: which segment we are in (0 for the first segment, 1 for the second, etc.)
      - block_type: one of "pair", "mirror", or "straight"
      - pos_in_block: the position within the block (1, 2, 3, …)
    """
    if seg_index == 0:
        return word

    # EXAMPLE transformations (illustrative only). Adjust to your real needs:
    if seg_index == 1:
        if word == "Ganna-Patim" and block_type in ["mirror", "straight"]:
            return "Gana-Pathi-gum"
        else:
            return word
    elif seg_index == 2:
        if pos_in_block == 1 and word == "Ganna-Patim":
            return "Gana-Pathigum"
        if pos_in_block == 3 and word == "Kavim" and block_type == "mirror":
            return "Kavi-gum"
        return word

    return word


def build_block(seg_index, block_type, words):
    """
    For a given segment (seg_index) use the overall word list to build a block.
    For segment seg_index, the base words (by overall position) are:
      p1 = seg_index + 1, p2 = seg_index + 2, p3 = seg_index + 3.
    """
    p1 = seg_index + 1
    p2 = seg_index + 2
    p3 = seg_index + 3

    if block_type == "pair":
        pattern = [p1, p2, p2, p1]
    elif block_type == "mirror":
        pattern = [p1, p2, p3, p3, p2, p1]
    elif block_type == "straight":
        pattern = [p1, p2, p3]
    else:
        pattern = []

    block_words = []
    for idx, overall_pos in enumerate(pattern, start=1):
        if overall_pos - 1 < len(words):
            original_word = words[overall_pos - 1]
            transformed = transform_word(original_word, overall_pos, seg_index, block_type, idx)
            block_words.append(transformed)
        else:
            block_words.append("?")
    return " ".join(block_words)


def transform_mantra(mantra_text):
    """
    Convert the original mantra into its ghanam version.
    Removes "|" markers, splits into words, then for each segment:
      1) pair block
      2) mirror block
      3) straight block
    """
    # Remove "|" and split into words
    words = [w for w in mantra_text.replace("||", "").replace("|", "").split() if w]

    output_segments = []
    for seg_index in range(len(words) - 2):
        block1 = build_block(seg_index, "pair", words)
        block2 = build_block(seg_index, "mirror", words)
        block3 = build_block(seg_index, "straight", words)
        segment_text = "\n".join([block1, block2, block3])
        output_segments.append(segment_text)

    return "\n\n".join(output_segments)

# -- JSON API for Next.js (or other front ends) --

@app.route("/transform", methods=["POST"])
def transform_endpoint():
    """
    Expects a JSON payload:
      {
        "mantra": "some text with optional | markers"
      }
    Returns:
      {
        "ghanam": "the transformed text"
      }
    """
    data = request.get_json()
    if not data or "mantra" not in data:
        return jsonify({"error": "No mantra provided"}), 400

    mantra_text = data["mantra"]
    ghanam = transform_mantra(mantra_text)
    return jsonify({"ghanam": ghanam})

# -- Optional: Retain Original HTML-Rendering Route --

HTML_TEMPLATE = """
<!doctype html>
<html>
  <head>
    <title>Mantra to Ghanam Converter</title>
    <style>
      body { font-family: sans-serif; margin: 2em; }
      textarea { font-size: 1.1em; width: 100%; }
      pre { background: #f0f0f0; padding: 1em; white-space: pre-wrap; }
    </style>
  </head>
  <body>
    <h1>Mantra to Ghanam Converter</h1>
    <form method="post">
      <p>Paste your mantra below:</p>
      <textarea name="mantra" rows="10">{{ mantra }}</textarea><br><br>
      <input type="submit" value="Convert to Ghanam">
    </form>
    {% if ghanam %}
    <h2>Ghanam Version:</h2>
    <pre>{{ ghanam }}</pre>
    {% endif %}
  </body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    ghanam = ""
    mantra = ""
    if request.method == "POST":
        mantra = request.form.get("mantra", "")
        ghanam = transform_mantra(mantra)
    return render_template_string(HTML_TEMPLATE, ghanam=ghanam, mantra=mantra)


# -- Entry Point --

if __name__ == "__main__":
    # Runs the Flask app on http://127.0.0.1:5000/
    app.run(debug=True, port=5000)
