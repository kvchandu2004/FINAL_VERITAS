import fitz  # PyMuPDF
from fastapi import HTTPException
import logging
import re

logger = logging.getLogger(__name__)

def clean_page_text(text: str) -> str:
    """
    Remove page numbers, headers, footers, and excessive whitespace.
    This ensures the AI doesn't get confused by repetitive document noise.
    """
    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        # 1. Skip pure numeric lines (usually page numbers)
        if re.fullmatch(r"\d+", line):
            continue

        # 2. Skip very short fragments (headers/footers/artifact noise)
        if len(line) < 3:
            continue
            
        # 3. Skip repetitive IEEE/Conference headers (Optional/Customizable)
        if "IEEE" in line or "Conference" in line:
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

def extract_text_from_pdf(file_path: str) -> dict:
    """
    Extract text content and metadata from PDF file.
    Returns dictionary with text, metadata, and page_count.
    """
    print("ivide")
    try:
        doc = fitz.open(file_path)
        print(doc)
        
        # Extract metadata
        metadata = {
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "keywords": doc.metadata.get("keywords", ""),
            "creation_date": doc.metadata.get("creationDate", ""),
        }
        print(metadata)
        # Extract text from all pages
        full_text = ""
        page_texts = []
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            raw_text = page.get_text("text")
            
            # --- APPLY CLEANING ---
            cleaned_text = clean_page_text(raw_text)
            
            page_texts.append({
                "page_number": page_num + 1,
                "text": cleaned_text
            })
            
            # Append to full text without adding artificial "--- Page X ---" markers
            # to keep the flow natural for the AI model.
            full_text += "\n" + cleaned_text
        
        doc.close()
        
        return {
            "full_text": full_text.strip(),
            "page_texts": page_texts,
            "metadata": metadata,
            "page_count": len(page_texts)
        }
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to extract text from PDF: {str(e)}"
        )
