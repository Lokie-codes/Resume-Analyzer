from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from utils.text_processing import sanitize_text
import PyPDF2
import docx

app = FastAPI()

@app.post("/analyze")
async def analyze_cv(
    resume_content: str = Form(None),
    resume_file: UploadFile = File(None),
    job_description_content: str = Form(None),
    job_description_file: UploadFile = File(None)
):
    if not (resume_content or resume_file):
        raise HTTPException(status_code=400, detail="Resume cannot be empty")
    if not (job_description_content or job_description_file):
        raise HTTPException(status_code=400, detail="Job Description cannot be empty")
    try:
        if resume_file:
            resume_content = await extract_text_from_pdf(resume_file)
        if job_description_file:
            job_description_content = await extract_text_from_pdf(job_description_file)
        job_description_blocks = sanitize_text(job_description_content)
        resume_blocks = sanitize_text(resume_content)

        analysis_response = {
            "job_description": job_description_content,
            "resume": resume_content,
            "matches": [],
            "missing": [],
            "score": 0
        }

        job_description_keys, job_description_count = extract_unique_words(job_description_blocks)
        resume_keys = extract_unique_words(resume_blocks)[0]

        # Calculate matches and mismatches
        analysis_response["matches"] = job_description_keys.intersection(resume_keys)
        analysis_response["missing"] = job_description_keys.difference(resume_keys)

        if job_description_count > 0:
            analysis_response["score"] = (len(analysis_response["matches"]) / job_description_count) * 100
            
        return analysis_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def extract_text_from_file(uploaded_file: UploadFile) -> str:
    file_extension = uploaded_file.filename.split('.')[-1].lower()
    if file_extension == 'pdf':
        return await extract_text_from_pdf(uploaded_file)
    elif file_extension == 'docx':
        return extract_text_from_docx(uploaded_file)
    elif file_extension == 'txt':
        return await extract_text_from_txt(uploaded_file)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

async def extract_text_from_pdf(uploaded_file: UploadFile) -> str:
    pdf_text = ""
    try:
        reader = PyPDF2.PdfReader(uploaded_file.file)  # Use the file-like object directly
        for page in reader.pages:
            pdf_text += page.extract_text() or ""  # Handle None cases
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF file: {str(e)}")
    return pdf_text

def extract_text_from_docx(uploaded_file: UploadFile) -> str:
    docx_text = ""
    try:
        doc = docx.Document(uploaded_file.file)
        for paragraph in doc.paragraphs:
            docx_text += paragraph.text + "\n"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading DOCX file: {str(e)}")
    return docx_text

async def extract_text_from_txt(uploaded_file: UploadFile) -> str:
    try:
        contents = await uploaded_file.read()
        return contents.decode('utf-8')  # Decode to string
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading TXT file: {str(e)}")


def extract_unique_words(blocks):
    unique_words = set()
    total_word_count = 0
    
    for block in blocks.values():
        words = block.split()
        unique_words.update(words)
        total_word_count += len(words)

    return unique_words, total_word_count
