from fasthtml.common import *
import base64
from io import BytesIO
from PIL import Image as PILImage

# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = """
:root {
  --bg: #f7f4ef;
  --ink: #1a1814;
  --muted: #6b6760;
  --accent: #c84b2f;
  --border: #dedad4;
  --card: #ffffff;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg);
  color: var(--ink);
  font-family: 'DM Sans', sans-serif;
  font-size: 17px;
  line-height: 1.7;
}

/* NAV */
nav {
  display: flex;
  justify-content: space-between;
  padding: 18px 50px;
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  background: var(--bg);
}

.nav-logo {
  font-family: monospace;
  font-size: 12px;
  color: var(--muted);
}

/* HERO */
.hero {
  max-width: 800px;
  margin: 120px auto 80px;
  padding: 0 30px;
}

h1 {
  font-family: serif;
  font-size: 56px;
  margin-bottom: 20px;
}

h2 {
  font-family: serif;
  font-size: 32px;
  margin-bottom: 20px;
}

h3 { margin-top: 25px; }

p {
  max-width: 650px;
  margin-bottom: 16px;
}

/* SECTION */
section {
  max-width: 800px;
  margin: 0 auto;
  padding: 80px 30px;
  border-top: 1px solid var(--border);
}

.section-label {
  font-size: 11px;
  color: var(--accent);
  margin-bottom: 10px;
}

/* CALLOUT */
.callout {
  background: #f5ede9;
  padding: 15px;
  border-left: 4px solid var(--accent);
  margin: 20px 0;
}

/* CODE */
.code {
  background: #1a1814;
  color: #e8e4dd;
  padding: 18px;
  border-radius: 8px;
  margin: 20px 0;
  overflow-x: auto;
  font-family: monospace;
  font-size: 13px;
}

/* UPLOAD */
.upload {
  border: 2px dashed var(--border);
  padding: 40px;
  text-align: center;
  background: var(--card);
  border-radius: 10px;
}

button {
  margin-top: 20px;
  padding: 10px 20px;
  background: black;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.result {
  margin-top: 30px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
}

.caption {
  padding: 20px;
  font-style: italic;
}
"""

# ── APP SETUP ─────────────────────────────────────────────────────────────────
app, rt = fast_app(
    hdrs=[
        Link(rel="preconnect", href="https://fonts.googleapis.com"),
        Link(
            rel="stylesheet",
            href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500&display=swap",
        ),
        Style(CSS),
    ]
)

# ── MODEL ─────────────────────────────────────────────────────────────────────
_processor = None
_model = None


def get_model():
    global _processor, _model
    if _processor is None:
        from transformers import BlipProcessor, BlipForConditionalGeneration

        _processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )
        _model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )
    return _processor, _model


def generate_alt_text(image):
    import torch

    processor, model = get_model()
    inputs = processor(image, return_tensors="pt")
    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=60)
    return processor.decode(output[0], skip_special_tokens=True)


def CodeBlock(code):
    return Div(code, cls="code")


# ── ROUTES ────────────────────────────────────────────────────────────────────
@rt("/")
def home():
    return Html(
        Body(
            Nav(Span("alt-text / ml-final", cls="nav-logo")),
            # HERO
            Div(
                P("Machine Learning · Spring 2026", cls="section-label"),
                H1("Automatic Alt-Text Generator"),
                P(
                    "A narrative ML project exploring accessibility and vision-language models."
                ),
                cls="hero",
            ),
            # PROJECT FRAMING
            Section(
                P("Project Framing", cls="section-label"),
                H2("A narrative, interactive project"),
                P(
                    "This project combines explanation, experiments, and a live demo into one experience."
                ),
                Div(
                    "This is both a technical system and a UX artifact shaped by accessibility.",
                    cls="callout",
                ),
            ),
            # MODEL
            Section(
                P("Model", cls="section-label"),
                H2("BLIP Image Captioning"),
                P("We use a pretrained model from Hugging Face."),
                CodeBlock(
                    """from transformers import BlipProcessor, BlipForConditionalGeneration

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")"""
                ),
                CodeBlock(
                    """def generate_alt_text(image):
    inputs = processor(image, return_tensors="pt")
    output = model.generate(**inputs, max_new_tokens=60)
    return processor.decode(output[0], skip_special_tokens=True)"""
                ),
            ),
            # PROCESSING
            Section(
                P("Image Processing", cls="section-label"),
                H2("Preprocessing experiments"),
                CodeBlock(
                    """from PIL import ImageEnhance
import numpy as np

def adjust_contrast(image, factor):
    return ImageEnhance.Contrast(image).enhance(factor)

def add_noise(image):
    arr = np.array(image)
    noise = np.random.normal(0, 25, arr.shape)
    return Image.fromarray(np.clip(arr + noise, 0, 255).astype('uint8'))"""
                ),
                P("These transformations test how robust the model is."),
            ),
            # TRY IT
            Section(
                P("Try it", cls="section-label"),
                H2("Upload an image"),
                Form(
                    Div(Input(type="file", name="image"), cls="upload"),
                    Button("Generate"),
                    enctype="multipart/form-data",
                    hx_post="/generate",
                    hx_target="#result",
                ),
                Div(id="result"),
            ),
        )
    )


@rt("/generate")
async def generate(image: UploadFile):
    data = await image.read()
    img = PILImage.open(BytesIO(data)).convert("RGB")

    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode()

    caption = generate_alt_text(img)

    return Div(
        Img(src=f"data:image/jpeg;base64,{img_b64}"),
        Div(caption, cls="caption"),
        cls="result",
    )


serve(port=5002)
