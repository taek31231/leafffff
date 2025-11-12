import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# --- 설정 및 제목 ---
st.set_page_config(page_title="🌱 식물 식별기", layout="centered")
st.title("🌱 Pl@ntNet 기반 식물 식별 앱")
st.subheader("사진을 업로드하면 Pl@ntNet API를 통해 식물 종을 식별합니다.")

# ⚠️ API 키
API_KEY = "2b10R9ZrSaICw0NXpyKPHagbO"
PLANTNET_URL = "https://my-api.plantnet.org/v2/identify/all"

# --- 식물 식별 함수 (Organs를 폼 데이터로 전송하도록 수정) ---
def identify_plant(uploaded_file, api_key):
    """
    Pl@ntNet API에 이미지를 전송하고 식별 결과를 반환합니다.
    """
    # ⚠️ 파일 포인터를 처음으로 돌림
    uploaded_file.seek(0) 
    
    # 1. 파일 데이터 준비 (files 딕셔너리)
    # Streamlit 파일 객체에서 순수한 바이트 데이터를 읽습니다.
    files = {
        'images': (uploaded_file.name, uploaded_file.read(), uploaded_file.type)
    }
    
    # 2. 쿼리 파라미터 준비 (params 딕셔너리)
    params = {
        'api-key': api_key,
    }
    
    # 3. 폼 데이터 파라미터 준비 (data 딕셔너리)
    # organs 및 project를 URL 쿼리가 아닌 폼 데이터로 전송하도록 시도
    data = {
        'project': 'all',
        # organs를 쉼표로 구분된 문자열로 전송
        'organs': 'flower,leaf,bark,fruit' 
    }
    
    with st.spinner('🔎 식물 식별 중... 잠시만 기다려 주세요.'):
        try:
            # API로 POST 요청 보내기: URL 쿼리(api-key)와 files/data(이미지/organs/project)를 분리 전송
            response = requests.post(
                PLANTNET_URL, 
                params=params, # URL 쿼리 파라미터 (API Key)
                files=files,   # 이미지 파일
                data=data      # 추가 폼 데이터 (organs, project)
            )
            response.raise_for_status() # HTTP 오류가 발생하면 예외 발생

            return response.json()

        except requests.exceptions.RequestException as e:
            st.error(f"API 요청 오류가 발생했습니다. 상세: {e}")
            # 서버가 보낸 구체적인 응답 본문을 확인해 볼 수도 있습니다.
            # st.error(f"서버 응답: {response.text}") 
            st.warning("요청 구조를 다시 확인해주세요.")
            return {"error": f"API 요청 중 오류 발생: {e}"}

# --- 메인 앱 로직 (생략: 변경 없음) ---
st.info("API 키가 설정되었습니다. 이제 식물 사진을 업로드해 주세요.")
uploaded_file = st.file_uploader("📷 식물 사진을 업로드하세요", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 1. 업로드된 이미지 처리 및 표시
    try:
        # PIL.Image.open은 file-like object를 받으므로 seek(0) 없이 사용 가능
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 이미지", use_column_width=True)
        
    except Exception as e:
        st.error(f"이미지 파일을 처리하는 중 오류가 발생했습니다. 상세 오류: {e}")
        st.stop()
    
    # 2. 식별 버튼
    if st.button("✨ 식별 시작"):
        # 3. API 요청 및 결과 표시
        result = identify_plant(uploaded_file, API_KEY)
        
        if 'error' in result:
            pass # 오류는 함수 내에서 이미 출력됨
        
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

            if len(result['results']) > 1:
                st.subheader("다른 가능성이 있는 결과")
                for r in result['results'][1:]:
                    r_score = r['score'] * 100
                    r_info = r['species']
                    r_common = r_info['commonNames'][0] if r_info.get('commonNames') else "알 수 없음"
                    st.write(f"- **{r_common}** (*{r_info['scientificName']}*): 신뢰도 {r_score:.2f}%")
        else:
            st.warning("😓 식물을 식별하지 못했습니다. 더 명확한 사진을 시도해 보세요.")
