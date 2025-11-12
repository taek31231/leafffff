import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# --- 설정 및 제목 ---
st.set_page_config(page_title="🌱 식물 식별기", layout="centered")
st.title("🌱 Pl@ntNet 기반 식물 식별 앱")
st.subheader("사진을 업로드하면 Pl@ntNet API를 통해 식물 종을 식별합니다.")

# --- ⚠️ API 키 입력 (Streamlit Secrets 사용 권장) ---
# **주의:** 실제 서비스 시에는 API 키가 코드에 노출되지 않도록
# Streamlit Secrets (secrets.toml) 파일에 저장하여 사용해야 합니다.
# 예시: API_KEY = st.secrets["plantnet"]["api_key"]
# 지금은 개발 편의를 위해 사용자에게 직접 입력받거나, 테스트 키를 사용해 주세요.
# 만약 키를 알고 있다면 직접 입력해도 됩니다.
API_KEY = st.sidebar.text_input("Pl@ntNet API Key를 입력하세요:", type="password")
PLANTNET_URL = "https://my-api.plantnet.org/v2/identify/all"

# --- 식물 식별 함수 ---
def identify_plant(image_data, api_key):
    """
    Pl@ntNet API에 이미지를 전송하고 식별 결과를 반환합니다.
    """
    if not api_key:
        return {"error": "API 키가 입력되지 않았습니다."}

    # API 요청을 위한 데이터 준비 (multipart/form-data)
    files = {
        # 'images'는 Pl@ntNet API가 요구하는 필드 이름입니다.
        'images': ('plant_image.jpg', image_data, 'image/jpeg')
    }

    # API 요청 파라미터
    params = {
        'api-key': api_key,
        # 'project'는 전 세계 모든 식물 종을 대상으로 식별을 요청
        'project': 'all' 
    }
    
    # 식별 중 표시
    with st.spinner('🔎 식물 식별 중... 잠시만 기다려 주세요.'):
        try:
            # API로 POST 요청 보내기
            response = requests.post(PLANTNET_URL, params=params, files=files)
            response.raise_for_status() # HTTP 오류가 발생하면 예외 발생

            return response.json()

        except requests.exceptions.RequestException as e:
            st.error(f"API 요청 오류가 발생했습니다: {e}")
            return {"error": f"API 요청 중 오류 발생: {e}"}

# --- 메인 앱 로직 ---
uploaded_file = st.file_uploader("📷 식물 사진을 업로드하세요", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 1. 업로드된 이미지 처리
    try:
        # 이미지를 PIL 객체로 변환하여 표시
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 이미지", use_column_width=True)
        
        # API 요청을 위해 이미지 데이터를 바이트 형태로 준비
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='JPEG')
        image_data = img_byte_arr.getvalue()
        
    except Exception as e:
        st.error("이미지 파일을 처리하는 중 오류가 발생했습니다. 파일을 확인해 주세요.")
        st.stop() # 오류 발생 시 실행 중지

    # 2. 식별 버튼
    if st.button("✨ 식별 시작"):
        if not API_KEY:
            st.warning("Pl@ntNet API Key를 입력해야 식별을 시작할 수 있습니다.")
        else:
            # 3. API 요청 및 결과 표시
            result = identify_plant(image_data, API_KEY)
            
            if 'error' in result:
                st.error(f"오류: {result['error']}")
            
            elif result.get('results'):
                st.success("✅ 식별 완료!")
                
                # 가장 높은 확률의 결과 추출
                best_match = result['results'][0]
                species_info = best_match['species']
                score = best_match['score'] * 100
                
                # 결과 표시
                st.markdown("---")
                
                # 🎈 가장 높은 결과
                st.header(f"가장 유사한 식물: {species_info['commonNames'][0] if species_info.get('commonNames') else '알 수 없음'}")
                st.markdown(f"**학명:** *{species_info['scientificName']}*")
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
