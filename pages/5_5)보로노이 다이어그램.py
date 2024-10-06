import streamlit as st


st.set_page_config(layout="wide")
if 'answer1' not in st.session_state:
    st.session_state['answer1']=0

st.header('보로노이 다이어그램')
col1, col2=st.columns([3,4])
with col1:
    st.image('./saves/voronoidiagram.gif')
with col2:
    st.image('./saves/voronoiex.png')
    st.write('출처:https://www.kdnuggets.com/2022/11/quick-overview-voronoi-diagrams.html')
st.write('보로노이 다이어그램이란 각 점까지의 거리가 가장 가까운 영역으로 분할한 그림입니다.')
st.write('보로노이 다이어그램은 자연에서도 관찰할 수 있는 패턴입니다. 또 실생활에서 구역을 나누는 방법으로도 쓰여요.')
st.write('예를 들어, 1854년 런던에서 발생한 콜레라 전염병 중에 의사 존 스노는 각 영역의 물 펌프 위치를 나타내는 보로노이 다이어그램을 사용하여 특정 펌프를 감염의 원인으로 식별하여 사망자 수를 세는 데 사용했습니다.')
st.write('보로노이 다이어그램을 그리는 방법 중에 하나는 수직이등분선을 이용하는 거에요.')


st.divider()
st.header('수직이등분선 구하기')


