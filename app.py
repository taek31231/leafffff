import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# --- 설정 및 제목 ---
st.set_page_config(page_title="🌱 식물 식별 앱", layout="centered")
st.title("🌱 Pl@ntNet 기반 식물 식별기")
st.subheader("사진을 업로드하고 식별 버튼을 눌러보세요.")

# ⚠️ API 키를 여기에 직접 삽입했습니다.
API_KEY = "2b10R9ZrSaICw0NXpyKPHagbO"
PLANTNET_URL = "https://my-api.plantnet.org/v2/identify/all"

# --- 식물 식별 함수 ---
def identify_plant(uploaded_file, api_key):
    """
    Pl@ntNet API에 이미지를 전송하고 식별 결과를 반환합니다.
    """
    # ⚠️ 파일 포인터를 처음으로 돌림: requests.post가 파일을 읽기 전에 필수
    uploaded_file.seek(0) 
    
    # 1. 파일 데이터 준비 (multipart/form-data)
    # 'images' 필드에 파일 이름, 바이트 데이터, MIME 타입을 포함
    files = {
        'images': (uploaded_file.name, uploaded_file.read(), uploaded_file.type)
    }

    # 2. URL 쿼리 파라미터 준비
    params = {
        'api-key': api_key,
        # project와 organs 파라미터는 400 Bad Request 오류를 일으키므로 제거함.
    }
    
    with st.spinner('🔎 식물 식별 중...'):
        try:
            # API로 POST 요청 보내기: URL 쿼리(api-key)와 files(이미지)만 전송
            response = requests.post(
                PLANTNET_URL, 
                params=params, 
                files=files
            )
            response.raise_for_status() # HTTP 오류가 발생하면 예외 발생

            return response.json()

        except requests.exceptions.RequestException as e:
            st.error(f"API 요청 오류가 발생했습니다. 상세: {e}")
            try:
                # 서버 응답 본문이 오류 원인을 알려줄 수 있으므로 출력
                st.error(f"서버 응답 본문: {response.text}")
            except Exception:
                pass
                
            return {"error": f"API 요청 중 오류 발생: {e}"}

# --- 메인 앱 로직 ---
st.markdown("---")
uploaded_file = st.file_uploader("📷 식물 사진을 업로드하세요", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 1. 업로드된 이미지 처리 및 표시
    try:
        # PIL을 사용해 이미지를 열고 표시
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 이미지", use_column_width=True)
        
    except Exception as e:
        st.error(f"이미지 파일을 처리하는 중 오류가 발생했습니다. 파일을 확인해 주세요. 상세 오류: {e}")
        st.stop()
    
    # 2. 식별 버튼
    if st.button("✨ 식별 시작", use_container_width=True):
        
        # 3. API 요청 및 결과 표시
        result = identify_plant(uploaded_file, API_KEY)
        
        if 'error' in result:
            st.error("식별에 실패했습니다. 위의 오류 메시지를 확인해주세요.")
            
        elif result.get('results'):
            st.success("✅ 식별 완료!")
            
            # 가장 높은 확률의 결과 추출
            best_match = result['results'][0]
            species_info = best_match['species']
            score = best_match['score'] * 100
            
            st.markdown("---")
            
            common_name = species_info['commonNames'][0] if species_info.get('commonNames') else "알 수 없음"
            scientific_name = species_info['scientificName']
            
            st.header(f"🌿 {common_name}")
            st.markdown(f"**학명:** *{scientific_name}*")
            st.metric(label="신뢰도", value=f"{score:.2f}%")

            # 추가 결과 표시 (최대 3개)
            if len(result['results']) > 1:
                st.subheader("다른 가능성이 있는 결과")
                for r in result['results'][1:4]: 
                    r_score = r['score'] * 100
                    r_info = r['species']
                    r_common = r_info['commonNames'][0] if r_info.get('commonNames') else "알 수 없음"
                    st.write(f"- **{r_common}** (*{r_info['scientificName']}*): 신뢰도 {r_score:.2f}%")
        else:
            st.warning("😓 식물을 식별하지 못했습니다. 더 명확한 사진을 시도해 보세요.")
