import asyncio
import tempfile
from pathlib import Path
from typing import Optional
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from slide_agent import SlideAgent

PPTX_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.presentationml.presentation"
)

app = FastAPI(title="Finstory API", version="1.0.0")
slide_agent = SlideAgent()


class SlideRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Narrative instructions")
    filename: Optional[str] = Field(
        default=None,
        description="Optional filename for the generated PPTX (must include .pptx)",
    )


@app.get("/")
async def root():
    return {"message": "Welcome to Finstory API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/slides")
async def create_slideshow(payload: SlideRequest):
    prompt = payload.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt must not be empty.")

    filename = payload.filename or f"finstory_{uuid4().hex}.pptx"
    if not filename.lower().endswith(".pptx"):
        raise HTTPException(
            status_code=400, detail="filename must end with the .pptx extension."
        )

    output_path = Path(tempfile.gettempdir(), filename)

    def _run_agent():
        return slide_agent.run(prompt=prompt, output_path=str(output_path))

    try:
        result = await asyncio.to_thread(_run_agent)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate slides: {exc}")

    report_path = result.get("report_path")
    if not report_path or not Path(report_path).exists():
        raise HTTPException(
            status_code=500, detail="Slide deck generation did not produce a file."
        )

    filename_to_download = Path(report_path).name
    return FileResponse(
        path=report_path,
        media_type=PPTX_MEDIA_TYPE,
        filename=filename_to_download,
        headers={
            "Content-Disposition": f'attachment; filename="{filename_to_download}"'
        },
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)