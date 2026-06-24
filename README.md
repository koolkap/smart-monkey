# ResumeForge AI

ResumeForge AI is a production-oriented Streamlit application for generating ATS-optimized, multilingual resumes from existing resume files, job descriptions, design references, and optional profile photos.

## Features

- Configurable LLM provider abstraction for Azure AI Foundry, OpenAI-compatible endpoints, Anthropic Claude, Google Gemini, and Ollama.
- Multi-file resume and job requirement ingestion.
- ATS scoring, keyword analysis, gap analysis, and recruiter visibility heuristics.
- Editable HTML resume generation with multiple themes.
- English and Korean localization using the selected LLM.
- PDF export hooks for print-ready A4 output.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

## Environment Configuration

ResumeForge AI now supports `.env` configuration with higher priority than the locally saved JSON settings file.

Priority order:

1. `.env` values
2. `data/settings.json`
3. dataclass defaults

Supported variables:

```env
RESUMEFORGE_PROVIDER=Ollama

AZURE_FOUNDRY_ENDPOINT=
AZURE_FOUNDRY_API_KEY=
AZURE_FOUNDRY_DEPLOYMENT=

OPENAI_COMPATIBLE_ENDPOINT=
OPENAI_COMPATIBLE_API_KEY=
OPENAI_COMPATIBLE_MODEL=

ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-3-5-sonnet-20240620

GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-pro

OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

## Project Structure

```text
app.py
components/
	ats_engine.py
	editor.py
	exporter.py
	uploader.py
providers/
	azure_foundry.py
	base.py
	claude.py
	factory.py
	gemini.py
	ollama.py
templates/html_themes/
	theme_registry.py
utils/
	ats_scorer.py
	image_parser.py
	models.py
	pdf_parser.py
	resume_builder.py
	storage.py
	translator.py
```

## Architecture

```mermaid
flowchart TD
		UI[Streamlit UI] --> Settings[Local Settings Store]
		UI --> Uploads[Resume and JD Uploaders]
		Uploads --> Parsers[PDF and Image Parsers]
		Settings --> Factory[Provider Factory]
		Factory --> Providers[Azure | OpenAI Compatible | Claude | Gemini | Ollama]
		Parsers --> Reconstruct[Profile Reconstruction Engine]
		Providers --> Reconstruct
		Reconstruct --> ATS[ATS Scoring Engine]
		Reconstruct --> Themes[HTML Theme Renderer]
		Reconstruct --> Translate[LLM Localization Engine]
		Themes --> Export[HTML and PDF Export]
```

## Deployment Instructions

### Local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### Streamlit Community Cloud

1. Push the repository to GitHub.
2. Set the main file to `app.py`.
3. Add provider secrets through the platform if you do not want to store them locally.

### Azure App Service or Container Hosting

1. Build a Python 3.11 environment.
2. Install `requirements.txt`.
3. Start with `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`.
4. Ensure WeasyPrint native dependencies are available in the image or host.

## Product Coverage

- Multi-file resume and requirement ingestion.
- ATS scoring, missing skills, weak keyword detection, and gap analysis.
- English and Korean resume generation using the selected LLM.
- Live JSON and field editing.
- Theme-based HTML resume rendering and PDF export.
- Provider adapter pattern with a frontend-only orchestration model.

## Notes

- Provider settings are stored locally in Streamlit session state and a local JSON settings file.
- If `.env` is present, its values override the local JSON settings file.
- PDF export uses WeasyPrint. On Windows, additional system libraries may be required depending on environment.

