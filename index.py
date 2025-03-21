import fitz  # PyMuPDF
from flask import Flask, request, send_file, render_template
import os

# Setup Flask
app = Flask(__name__, template_folder="../templates")
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# PDF Processing Function
def highlight_large_qty(pdf_path, output_path):
    doc = fitz.open(pdf_path)

    for page in doc:
        text_blocks = page.get_text("blocks")
        in_table = False

        for block in text_blocks:
            x0, y0, x1, y1, text, *_ = block

            # Check for the start of the table
            if "Description" in text and "Qty" in text:
                in_table = True
                continue

            # If in the table, look for quantities
            if in_table:
                # Skip headings or non-numeric blocks
                if not any(char.isdigit() for char in text):
                    continue

                # Ensure the block is likely a quantity
                if "Qty" in text or "Unit Price" in text or "Total" in text:
                    continue

                values = text.split()
                for val in values:
                    if val.isdigit() and int(val) > 1:
                        highlight_box = fitz.Rect(x0, y0, x1, y1)
                        page.draw_rect(highlight_box, color=(1, 0, 0), fill_opacity=0.4)
                        break

            # Check for the end of the table
            if "TOTAL" in text:
                in_table = False

    doc.save(output_path)

# Serve the HTML Page
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Handle File Upload
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file uploaded", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    input_pdf = os.path.join(UPLOAD_FOLDER, file.filename)
    output_pdf = os.path.join(UPLOAD_FOLDER, "highlighted_" + file.filename)

    file.save(input_pdf)
    highlight_large_qty(input_pdf, output_pdf)

    return send_file(output_pdf, as_attachment=True)

if __name__ == "__main__":
    # Remove the main block for Vercel deployment
    # app.run(host="0.0.0.0", port=port, debug=True)
    pass  # Vercel will handle the server
