from typing import List
from fastapi import UploadFile
import mimetypes
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tempfile
import os
import fitz
import pytesseract
from PIL import Image
import io
from langchain_community.document_loaders import PyMuPDFLoader



async def process_file(file: UploadFile, filename: str) -> List[str]:
    """
    Handles file processing based on its type using LangChain.
    """
    mime_type, _ = mimetypes.guess_type(filename)

    print('the mime type is', mime_type)

    if mime_type == "application/pdf":
        extractor = PdfExtractor()
        result = await extractor.process_pdf(file)
        return result
    elif mime_type in ["text/markdown", "text/plain"]:
        loader = TextLoader()
        return ["Hello", "World", "plain"]
    elif mime_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        return ["Hello", "World", "word"]
    else:
        raise ValueError("Unsupported file type.")

    return ["Hello", "World", "Romuald"]


class PdfExtractor:
    def __init__(self, lang: str = 'eng'):
        self.lang = lang
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators="\n",
            chunk_size=1000,
            chunk_overlap=50
        )

    async def process_pdf(self, file: UploadFile) -> List[str]:
        result: str = ''
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # Load and process PDF with LangChain
            loader = PyMuPDFLoader(tmp_path)
            pages = loader.load()
            
            # Process OCR separately since LangChain doesn't handle it directly
            doc = fitz.open(tmp_path)

            for page in pages:
                page_num = page.metadata['page']
                result += page.page_content

                # Extract and process images
                pdf_page = doc[page_num]
                image_texts = self._process_images(pdf_page)
                result += ' '.join(image_texts)

            result = result.replace('\t', ' ')

            texts = self.text_splitter.split_text(result)
            return texts

        finally:
            os.unlink(tmp_path)
            
    def _process_images(self, page: fitz.Page) -> List[str]:
        image_texts = []
        
        for img in page.get_images():
            try:
                xref = img[0]
                base_image = page.parent.extract_image(xref)
                image = Image.open(io.BytesIO(base_image["image"]))
                
                if image.mode not in ('L', 'RGB'):
                    image = image.convert('RGB')
                
                image_text = pytesseract.image_to_string(
                    image, 
                    lang=self.lang,
                    config='--psm 3'
                )
                
                if image_text.strip():
                    image_texts.append(image_text.strip())
                    
            except Exception as e:
                print(f"Error processing image: {str(e)}")
                continue
                
        return image_texts
