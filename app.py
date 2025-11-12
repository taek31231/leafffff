import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# --- 설정 및 제목 ---
st.set_page_config(page_title="🌱 식물 식별기", layout="centered")
st.title("🌱 Pl@ntNet 기반 식물 식별 앱")
st.subheader("사진을 업로드하면 Pl@ntNet API를 통해 식물 종을 식별합니다.")

# ⚠️ API 키를 코드에 직접 삽입했습니다.
API_KEY = "2b10R9ZrSaICw0NXpyKPHagbO"
PLANTNET_URL = "https://my-api.plantnet.org/v2/identify/all"

# --- 식물 식별 함수 (수정됨: uploaded_file을 직접 받음) ---
def identify_plant(uploaded_file, api_key):
    """
    Pl@ntNet API에 이미지를 전송하고 식별 결과를 반환합니다.
    """
    # ⚠️ Streamlit 파일 객체를 사용하기 위해 포인터를 처음으로 돌립니다.
    uploaded_file.seek(0)
    
    # API 요청을 위한 데이터 준비 (multipart/form-data)
    # files 딕셔너리 구조: {'필드 이름': (파일명, 파일 바이트 데이터, MIME 타입)}
    files = {
        'images': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
    }

    # API 요청 파라미터
    params = {
        'api-key': api_key,
        'project': 'all' 
    }
    
    with st.spinner('🔎 식물 식별 중... 잠시만 기다려 주세요.'):
        try:
            # API로 POST 요청 보내기
            response = requests.post(PLANTNET_URL, params=params, files=files)
            response.raise_for_status() # HTTP 오류가 발생하면 예외 발생

            return response.json()

        except requests.exceptions.RequestException as e:
            # 400 Bad Request 오류를 포함한 모든 요청 오류 처리
            st.error(f"API 요청 오류가 발생했습니다. 상세: {e}")
            st.warning("Pl@ntNet API가 요청 데이터를 올바르게 받지 못했습니다. 업로드한 파일 형식을 확인해주세요.")
            return {"error": f"API 요청 중 오류 발생: {e}"}

# --- 메인 앱 로직 ---
st.info("API 키가 설정되었습니다. 이제 식물 사진을 업로드해 주세요.")
uploaded_file = st.file_uploader("📷 식물 사진을 업로드하세요", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 1. 업로드된 이미지 처리 및 표시
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 이미지", use_column_width=True)
        
    except Exception as e:
        st.error(f"이미지 파일을 처리하는 중 오류가 발생했습니다. 상세 오류: {e}")
        st.stop()
    
    # 2. 식별 버튼
    if st.button("✨ 식별 시작"):
        # 3. API 요청 (업로드된 파일 객체 자체를 전달) 및 결과 표시
        result = identify_plant(uploaded_file, API_KEY)
        
        if 'error' in result:
            # 오류는 이미 identify_plant 함수 내에서 출력됨
            pass
        
        elif result.get('results'):
            st.success("✅ 식별 완료!")
            
            best_match = result['results'][0]
            species_info = best_match['species']
            score = best_match['score'] * 100
            
            st.markdown("---")
            
            common_name = species_info['commonNames'][0] if species_info.get('commonNames') else "알 수 없음"
            scientific_name = species_info['scientificName']
            
            st.header(f"가장 유사한 식물: {common_name}")
            st.markdown(f"**학명:** *{scientific_name}*")
            st.metric(label="신뢰도", value=f"{score:.2f}%")

            # 추가 결과 (선택 사항)
            if len(result['results']) > 1:
                st.subheader("다른 가능성이 있는 결과")
                for r in result['results'][1:]:
                    r_score = r['score'] * 100
                    r_info = r['species']
                    r_common = r_info['commonNames'][0] if r_info.get('commonNames') else "알 수 없음"
                    st.write(f"- **{r_common}** (*{r_info['scientificName']}*): 신뢰도 {r_score:.2f}%")
        else:
            st.warning("😓 식물을 식별하지 못했습니다. 더 명확한 사진을 시도해 보세요.")
