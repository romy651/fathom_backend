from sys import maxsize
from fastapi import APIRouter, File, HTTPException, UploadFile, Form

from model.schemas import PageContent
from services.file_handler import process_file


router = APIRouter(prefix="/process", tags=["Files"])

@router.post("/", response_model=PageContent)
async def process_file_upload(file: UploadFile = File(...), filename: str = Form(...)):
    """
    Endpoint to process an uploaded file and return chunks.
    """
    try:
        print('hello with file', filename)
        processed = await process_file(file, filename)
        print('the processed is', len(processed))
        
        return {"content": processed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
  

