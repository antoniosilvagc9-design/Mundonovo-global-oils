"""API local para geração demonstrativa de PowerPoint."""
from fastapi import FastAPI
from fastapi.responses import Response, FileResponse
from pathlib import Path
from demo_data import get_demo_data
from generator import generate_presentation

app = FastAPI(title="Mundo Novo Executive Report", version="0.1.0")

@app.get("/")
def dashboard():
    return FileResponse(Path(__file__).with_name("dashboard-demo.html"))

@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "demo"}

@app.get("/api/executive-report/preview")
def preview():
    return get_demo_data()

@app.post("/api/executive-report/generate")
def generate():
    content = generate_presentation(get_demo_data())
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": 'attachment; filename="mundo_novo_relatorio_demo.pptx"'},
    )
