from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import StreamingResponse
from PIL import Image
import io
from typing import List, Optional

app = FastAPI()
processed_image = None

@app.post("/process-image/")
async def process_image(
    file: UploadFile = File(...), 
    operations: List[str] = Form(...),
    rotate_angle: Optional[int] = Form(0)
):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Only JPEG and PNG are supported.")
    
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    
    for operation in operations:
        if operation == "grayscale":
            image = image.convert("L")
        elif operation == "rotate":
            image = image.rotate(rotate_angle, expand=True)
        elif operation == "resize":
            image = image.resize((300, 300))
    
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    
    global processed_image
    processed_image = buffer
    return {"message": "Image processed successfully"}

@app.get("/get-image/")
async def get_image():
    if not processed_image:
        raise HTTPException(status_code=404, detail="No image has been processed.")
    
    return StreamingResponse(processed_image, media_type="image/jpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
