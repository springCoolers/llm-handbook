import requests
import json
import pandas as pd
from pathlib import Path
import shutil
from datetime import datetime
import time

def send_csv_for_processing(csv_file_path, api_url="http://localhost:8000/process"):
    """
    CSV 파일을 API에 전송하여 처리하고 결과를 JSON과 CSV 파일로 저장합니다.
    
    Args:
        csv_file_path (str): 처리할 CSV 파일의 경로
        api_url (str): API 엔드포인트 URL
    """
    try:
        # 시작 시간 기록
        start_time = time.time()
        
        # 결과를 저장할 디렉토리 생성
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        
        # 현재 시간을 파일명에 포함
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 원본 CSV 파일을 results 디렉토리에 복사
        csv_filename = Path(csv_file_path).name
        csv_backup = results_dir / f"{csv_filename.rsplit('.', 1)[0]}_{timestamp}.csv"
        shutil.copy2(csv_file_path, csv_backup)
        print(f"원본 CSV 파일이 {csv_backup}에 저장되었습니다.")
        
        # 파일을 열어서 multipart/form-data 형식으로 전송
        with open(csv_file_path, 'rb') as file:
            # 파일 이름만 추출
            filename = Path(csv_file_path).name
            files = {'file': (filename, file, 'text/csv')}
            
            print(f"CSV 파일을 {api_url}로 전송 중...")
            # API 요청 보내기
            response = requests.post(api_url, files=files)
            
            # 응답 상태 확인
            response.raise_for_status()
            
            # JSON 응답 파싱
            result = response.json()
            
            # JSON 결과를 파일로 저장
            json_output = results_dir / f"processed_result_{timestamp}.json"
            with open(json_output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            # JSON 결과를 DataFrame으로 변환하고 CSV로 저장
            df = pd.DataFrame(result['results'])
            csv_output = results_dir / f"processed_result_{timestamp}.csv"
            df.to_csv(csv_output, index=False, encoding='utf-8')
            
            # 종료 시간 기록 및 총 소요 시간 계산
            end_time = time.time()
            total_time = end_time - start_time
            
            # 처리 결과 출력
            print(f"\n처리가 완료되었습니다.")
            print(f"원본 CSV 백업: {csv_backup}")
            print(f"JSON 결과 저장: {json_output}")
            print(f"CSV 결과 저장: {csv_output}")
            print(f"총 처리된 행 수: {result['metadata']['total_rows']}")
            print(f"사용된 모델: {result['metadata']['model']}")
            print(f"API 처리 시간: {result['metadata']['timestamp']}")
            print(f"전체 처리 시간: {total_time:.2f}초")
            
    except requests.exceptions.RequestException as e:
        print(f"API 요청 중 오류가 발생했습니다: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"JSON 응답 파싱 중 오류가 발생했습니다: {str(e)}")
    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    # 예제 사용법
    csv_file = "/Users/oldman/Library/CloudStorage/OneDrive-개인/001_Documents/001_TelePIX/000_workspace/02_PseudoLab/llm-handbook/dev/summarization/handbook-infra-data.csv"
    send_csv_for_processing(csv_file)
