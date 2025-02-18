from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import pandas as pd
from openai import OpenAI
import io
import os
import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client with default configuration
client = OpenAI(
    timeout=30.0,
    max_retries=2
)

# Default model to use
GPT_MODEL = "gpt-4o-mini"

# Create semaphore to limit concurrent API calls
API_SEMAPHORE = asyncio.Semaphore(3)  # Limit to 3 concurrent requests

# Create results directory if it doesn't exist
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

# Default prompt for summarization
SUMMARY_PROMPT = """You are an AI language model specialized in summarizing texts while preserving key information. Your task is to generate a structured summary.

**Input:**
Title: {제목}
Content: {본문}

**Instructions:**
- The summary must retain essential details without losing meaning.
- The output should be structured in two parts: 
  1. The original title.
  2. A detailed summary of the content.
- Ensure the summary is concise but complete.

**Output Format (Markdown):**
### {제목}

**Summary:** {요약된 본문}"""

# Default prompt for category classification
CATEGORY_PROMPT = """You are an AI model that categorizes content into predefined categories. Your task is to classify the given text into **one** of the following categories:

1. **논문 (Research Paper)** - Academic papers, studies, or research findings.
2. **모델 (Model)** - AI/ML models, architectures, or improvements.
3. **도구 (Tool)** - AI-related software, libraries, or frameworks.
4. **업데이트&트렌드 (Updates & Trends)** - News, developments, and AI/ML trends.

**Input:**
Title: {제목}
Content: {본문}

**Instructions:**
- Assign exactly **one** category from the list.
- Choose **논문** if the content discusses a research study or academic findings.
- Choose **모델** if the content discusses AI model development or architectures.
- Choose **도구** if the content introduces AI/ML tools or software.
- Choose **업데이트&트렌드** if the content reports industry trends or news.

**Output Format (Markdown):**
### {제목}

**Category:** {분류}
"""

# Default prompt for keyword extraction
KEYWORDS_PROMPT = """You are an AI model trained to extract distinct and relevant keywords from a given text. Your task is to generate **3 to 5 unique keywords** that best represent the content.

**Input:**
Title: {제목}
Content: {본문}

**Instructions:**   
- Identify 3 to 5 **distinct** keywords summarizing the content.
- Ensure the keywords are **MECE (Mutually Exclusive, Collectively Exhaustive)**.
- Avoid generic words and focus on domain-specific terms.
- Do not include redundant or overlapping keywords.

**Output Format (Markdown):**
### {제목}

**Keywords:** {키워드1}, {키워드2}, {키워드3}, {키워드4}, {키워드5}
"""

async def call_openai(prompt, title, content, max_retries=3):
    message = f"{prompt}\n\nTitle: {title}\nContent: {content}"
    
    async with API_SEMAPHORE:  # Use semaphore to limit concurrent requests
        for attempt in range(max_retries):
            try:
                logger.info(f"Sending request to OpenAI for title: {title[:50]}... (Attempt {attempt + 1}/{max_retries})")
                response = await asyncio.to_thread(
                    client.chat.completions.create,
                    model=GPT_MODEL,
                    messages=[{"role": "user", "content": message}],
                    temperature=0.7,
                )
                result = response.choices[0].message.content.strip()
                logger.info(f"Received response from OpenAI for title: {title[:50]}")
                return result
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    logger.error(f"OpenAI API Error for title '{title[:50]}' after {max_retries} attempts: {str(e)}")
                    return f"OpenAI API 오류: {str(e)}"
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for title '{title[:50]}': {str(e)}. Retrying...")
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff

async def process_row(row, index, results):
    try:
        title = str(row["제목"])
        content = str(row["본문"])
        
        logger.info(f"Processing row {index} - Title: {title[:50]}")
        
        # Process each API call with individual timeouts
        try:
            logger.info(f"Row {index}: Starting summary generation")
            summary = await asyncio.wait_for(
                call_openai(SUMMARY_PROMPT, title, content),
                timeout=180  # Increased timeout to 3 minutes
            )
        except asyncio.TimeoutError:
            logger.error(f"Timeout generating summary for row {index}")
            summary = "요약 생성 중 시간 초과. 다시 시도해주세요."

        try:
            logger.info(f"Row {index}: Starting category classification")
            category = await asyncio.wait_for(
                call_openai(CATEGORY_PROMPT, title, content),
                timeout=180
            )
        except asyncio.TimeoutError:
            logger.error(f"Timeout generating category for row {index}")
            category = "분류 생성 중 시간 초과. 다시 시도해주세요."

        try:
            logger.info(f"Row {index}: Starting keyword extraction")
            keywords = await asyncio.wait_for(
                call_openai(KEYWORDS_PROMPT, title, content),
                timeout=180
            )
        except asyncio.TimeoutError:
            logger.error(f"Timeout generating keywords for row {index}")
            keywords = "키워드 생성 중 시간 초과. 다시 시도해주세요."
        
        # Store results
        results[index] = {
            "요약문": summary,
            "분류": category,
            "키워드": keywords
        }
        logger.info(f"Row {index}: Completed processing")
        
    except Exception as e:
        logger.error(f"Error processing row {index}: {str(e)}")
        results[index] = {
            "요약문": f"처리 중 오류 발생: {str(e)}",
            "분류": f"처리 중 오류 발생: {str(e)}",
            "키워드": f"처리 중 오류 발생: {str(e)}"
        }

app = FastAPI()

@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    logger.info(f"Received file: {file.filename}")
    
    if not file.filename.endswith((".xlsx", ".xls")):
        logger.error(f"Invalid file type: {file.filename}")
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an Excel file.")
    
    try:
        # Read the file in chunks
        logger.info("Reading file contents")
        chunk_size = 8192
        contents = b""
        chunks_read = 0
        while chunk := await file.read(chunk_size):
            contents += chunk
            chunks_read += 1
            if chunks_read % 10 == 0:  # Log every 10 chunks
                logger.info(f"Read {chunks_read * chunk_size / 1024:.1f}KB of data")
            
        logger.info("Loading Excel file into pandas")
        df = pd.read_excel(io.BytesIO(contents), sheet_name="트렌드 (영상)")
        logger.info(f"Loaded Excel file with {len(df)} rows")
        
    except Exception as e:
        logger.error(f"File reading error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reading Excel file: {str(e)}")
    
    if "제목" not in df.columns or "본문" not in df.columns:
        logger.error("Required columns not found in Excel file")
        raise HTTPException(status_code=400, detail="Excel file must contain '제목' and '본문' columns.")
    
    # Initialize empty columns for our new data
    df["요약문"] = ""
    df["분류"] = ""
    df["키워드"] = ""
    
    try:
        # Process all rows concurrently
        logger.info("Starting concurrent processing of all rows")
        results = {}
        tasks = [process_row(row, index, results) for index, row in df.iterrows()]
        await asyncio.gather(*tasks)
        
        # Update DataFrame with results
        logger.info("Updating DataFrame with results")
        for index, result in results.items():
            df.at[index, "요약문"] = result["요약문"]
            df.at[index, "분류"] = result["분류"]
            df.at[index, "키워드"] = result["키워드"]
        
        # Convert DataFrame to JSON
        logger.info("Preparing JSON response")
        json_data = []
        for _, row in df.iterrows():
            # Convert the entire row to a dictionary, handling all columns
            row_dict = row.to_dict()
            # Convert any non-serializable objects to strings
            for key, value in row_dict.items():
                if pd.isna(value):  # Handle NaN values
                    row_dict[key] = None
                elif isinstance(value, pd.Timestamp):  # Handle datetime objects
                    row_dict[key] = value.isoformat()
                elif not isinstance(value, (str, int, float, bool, type(None))):  # Handle other objects
                    row_dict[key] = str(value)
            json_data.append(row_dict)
        
        # Create results object with metadata
        results_object = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "filename": file.filename,
                "total_rows": len(df),
                "model": GPT_MODEL
            },
            "results": json_data
        }
        
        # Save to fixed JSON filename
        output_path = Path("processed_result.json")
        
        logger.info(f"Saving results to {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results_object, f, ensure_ascii=False, indent=2)
        
        logger.info("Sending response")
        return JSONResponse(
            content=results_object,
            headers={
                "Content-Disposition": "attachment; filename=processed_result.json",
                "Content-Type": "application/json; charset=utf-8"
            }
        )
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=8000)