import requests
import json

def send_excel_for_processing(excel_file_path, api_url="http://localhost:8000/process"):
    """
    Excel 파일을 API에 전송하여 처리하고 결과를 JSON 파일로 저장합니다.
    
    Args:
        excel_file_path (str): 처리할 Excel 파일의 경로
        api_url (str): API 엔드포인트 URL
    """
    try:
        # 파일을 열어서 multipart/form-data 형식으로 전송
        with open(excel_file_path, 'rb') as file:
            files = {'file': (excel_file_path, file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            print(f"Excel 파일을 {api_url}로 전송 중...")
            # API 요청 보내기
            response = requests.post(api_url, files=files)
            
            # 응답 상태 확인
            response.raise_for_status()
            
            # JSON 응답 파싱
            result = response.json()
            
            # 결과를 JSON 파일로 저장
            output_file = 'processed_result.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            # 처리 결과 출력
            print(f"\n처리가 완료되었습니다. 결과가 {output_file}에 저장되었습니다.")
            print(f"총 처리된 행 수: {result['metadata']['total_rows']}")
            print(f"사용된 모델: {result['metadata']['model']}")
            print(f"처리 시간: {result['metadata']['timestamp']}")
            
    except requests.exceptions.RequestException as e:
        print(f"API 요청 중 오류가 발생했습니다: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"JSON 응답 파싱 중 오류가 발생했습니다: {str(e)}")
    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    # 예제 사용법
    excel_file = "/Users/oldman/Library/CloudStorage/OneDrive-개인/001_Documents/001_TelePIX/000_workspace/02_PseudoLab/01_summarization/핸드북 인프라 데이터 정리.xlsx"
    send_excel_for_processing(excel_file)
