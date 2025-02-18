# Excel Summary Generator API

This API service processes Excel files containing text content and generates summaries, categories, and keywords using OpenAI's GPT model.

## Building and Running with Docker

1. Build the Docker image:
```bash
docker build -t excel-summary-api .
```

2. Run the container:
```bash
docker run -p 8000:8000 --env-file .env excel-summary-api
```

## API Usage

Send a POST request to `/process` with an Excel file:

```bash
curl -X POST "http://localhost:8000/process" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_file.xlsx"
```

The API expects an Excel file with the following columns in the "트렌드 (영상)" sheet:
- 제목 (Title)
- 본문 (Content)

The API will return a CSV file containing the original columns plus:
- 요약문 (Summary)
- 분류 (Category)
- 키워드 (Keywords)

## Environment Variables

Create a `.env` file with:
```
OPENAI_API=your_openai_api_key
```
