# --- 식물 식별 함수 (project 파라미터 제거) ---
def identify_plant(uploaded_file, api_key):
    """
    Pl@ntNet API에 이미지를 전송하고 식별 결과를 반환합니다.
    """
    # ⚠️ 파일 포인터를 처음으로 돌림
    uploaded_file.seek(0) 
    
    # 1. 파일 데이터 준비 (files 딕셔너리)
    files = {
        # Streamlit이 제공하는 MIME 타입 사용
        'images': (uploaded_file.name, uploaded_file.read(), uploaded_file.type)
    }

    # 2. 쿼리 파라미터 준비 (params 딕셔너리)
    params = {
        'api-key': api_key,
        # ❌ "project" is not allowed 오류 해결: 'project': 'all' 파라미터를 제거합니다.
        # organs만 URL 쿼리로 전송
        'organs': 'flower,leaf,bark,fruit' 
    }
    
    with st.spinner('🔎 식물 식별 중... 잠시만 기다려 주세요.'):
        try:
            # API로 POST 요청 보내기
            response = requests.post(
                PLANTNET_URL, 
                params=params, # URL 쿼리 파라미터 (api-key, organs)
                files=files    # 이미지 파일
            )
            response.raise_for_status() # HTTP 오류가 발생하면 예외 발생

            return response.json()

        except requests.exceptions.RequestException as e:
            st.error(f"API 요청 오류가 발생했습니다. 상세: {e}")
            try:
                st.error(f"서버 응답 본문: {response.text}")
            except Exception:
                pass
                
            st.warning("요청 구조를 다시 확인해주세요.")
            return {"error": f"API 요청 중 오류 발생: {e}"}

# --- (메인 앱 로직은 변경 없음) ---
# ...
