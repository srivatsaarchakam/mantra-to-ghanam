from flask import Flask, render_template_string, request

app = Flask(__name__)

def transform_word(word, overall_pos, seg_index, block_type, pos_in_block):
    """
    Transform the original word based on:
      - overall_pos: the word’s position in the full mantra (1-indexed)
      - seg_index: which segment we are in (0 for the first segment, 1 for the second, etc.)
      - block_type: one of "pair", "mirror", or "straight"
      - pos_in_block: the position within the block (1, 2, 3, …)
      
    For segment 0 (the first segment) no change is needed.
    For later segments you can apply modifications. (The examples below are only illustrative.)
    """
    # For the first segment, return the word unchanged.
    if seg_index == 0:
        return word

    # Example transformation rules (fill in or adjust these as needed):
    if seg_index == 1:
        # For segment 2 (overall positions 2–4)
        # In the mirror and straight blocks, change "Ganna-Patim" to "Gana-Pathi-gum"
        if word == "Ganna-Patim" and block_type in ["mirror", "straight"]:
            return "Gana-Pathi-gum"
        else:
            return word

    elif seg_index == 2:
        # For segment 3 (overall positions 3–5)
        # For example, if the first word of the block is "Ganna-Patim", change it to "Gana-Pathigum"
        # and if the third word is "Kavim", change it to "Kavi-gum" (in mirror blocks only).
        if pos_in_block == 1 and word == "Ganna-Patim":
            # In the pair and mirror blocks sometimes the initial word changes
            return "Gana-Pathigum"
        if pos_in_block == 3 and word == "Kavim" and block_type == "mirror":
            return "Kavi-gum"
        return word

    # Add further rules for seg_index >= 3 as needed…
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
    # The pattern list contains overall positions (1-indexed).
    for idx, overall_pos in enumerate(pattern, start=1):
        # Make sure we have a word at this overall position.
        if overall_pos - 1 < len(words):
            original_word = words[overall_pos - 1]
            # Transform the word as needed.
            transformed = transform_word(original_word, overall_pos, seg_index, block_type, idx)
            block_words.append(transformed)
        else:
            block_words.append("?")
    return " ".join(block_words)

def transform_mantra(mantra_text):
    """
    Convert the original mantra into its ghanam version.
    (Here we remove the "|" markers and split on whitespace. You might wish to refine
     the splitting if your original mantra uses punctuation for grouping.)
    """
    # Remove "|" and "||" and split into words.
    words = [w for w in mantra_text.replace("||", "").replace("|", "").split() if w]

    output_segments = []
    # For each segment we need at least three overall words.
    for seg_index in range(len(words) - 2):
        block1 = build_block(seg_index, "pair", words)
        block2 = build_block(seg_index, "mirror", words)
        block3 = build_block(seg_index, "straight", words)
        segment_text = "\n".join([block1, block2, block3])
        output_segments.append(segment_text)
    return "\n\n".join(output_segments)

# --- Flask Web Front End ---
HTML_TEMPLATE = """
<!doctype html>
<html>
  <head>
    <title>Mantra to Ghanam Converter</title>
    <style>
      body { font-family: sans-serif; margin: 2em; }
      textarea { font-size: 1.1em; }
      pre { background: #f0f0f0; padding: 1em; white-space: pre-wrap; }
    </style>
  </head>
  <body>
    <h1>Mantra to Ghanam Converter</h1>
    <form method="post">
      <p>Paste your mantra below:</p>
      <textarea name="mantra" rows="10" cols="60">{{ mantra }}</textarea><br>
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

if __name__ == "__main__":
    app.run(debug=True)
