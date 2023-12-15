import streamlit as st
import pandas as pd
from PIL import Image
import folium
from folium import Marker
from streamlit_folium import st_folium, folium_static
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

import requests
from branca.colormap import linear
from scipy.spatial import Voronoi, voronoi_plot_2d
import numpy as np
from shapely.geometry import MultiPoint, Point, Polygon
import geopandas as gpd

from pandas import json_normalize
from streamlit_drawable_canvas import st_canvas

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
st.write('보로노이 다이어그램이란 각 점까지의 거리가 가장 영역으로 분할한 그림입니다.')
st.write('보로노이 다이어그램은 자연에서도 관찰할 수 있는 패턴입니다. 또 실생활에서 구역을 나누는 방법으로도 쓰여요.')
st.write('예를 들어, 1854년 런던에서 발생한 콜레라 전염병 중에 의사 존 스노는 각 영역의 물 펌프 위치를 나타내는 보로노이 다이어그램을 사용하여 특정 펌프를 감염의 원인으로 식별하여 사망자 수를 세는 데 사용했습니다.')
st.write('보로노이 다이어그램을 그리는 방법 중에 하나는 수직이등분선을 이용하는 거에요.')


st.divider()
st.header('수직이등분선 구하기')
st.write('두 점 (1,5), (4,2)의 수직이등분선을 구해봅시다.')
st.write('노트 또는 아래의 캔버스를 이용하세요.')
drawing_mode = st.sidebar.selectbox(
    "그리기 도구:", ("freedraw", "line", "transform")
)

stroke_width = st.sidebar.slider("크기: ", 1, 25, 3)

stroke_color = st.sidebar.color_picker("색: ")

st.write('1) 두 점 (1,5), (4,2)을 이은 직선은?')
col1,col2=st.columns([4,1])

with col1:
    
    canvas_result = st_canvas(stroke_width=stroke_width,stroke_color=stroke_color,drawing_mode=drawing_mode,update_streamlit=True,background_image=Image.open('./saves/좌표2.png'),width=800,key="canvas1")
with col2:
    st.write('y=ax+b에서 a와 b를<br>입력하세요', unsafe_allow_html=True)
    a1=st.number_input('a', min_value=-5.0, max_value=5.0, step=0.5,key='a')
    b1=st.number_input('b',min_value=-10.0, max_value=10.0, step=0.5,key='b')
    st.write(f'y={a1}x+{b1}')
    button1=st.button('확인하기',key='button1')
    if button1:
        if a1==-1 and b1==6:
            st.write('맞아요! 2) 문제로 넘어가세요')
        else:
            st.write('다시 확인해봅시다. <br>각 좌표의 평균을 이용하여 중점을 구하고, <br>좌표의 차이로 기울기를 구해야해요', unsafe_allow_html=True)
st.divider()
col3,col4=st.columns([4,1])
with col3:
    st.write('2) 두 점 (1,5), (4,2)을 이은 선분의 수직이등분선은?')

    canvas_res = st_canvas(drawing_mode='freedraw',update_streamlit=True,stroke_width=5,background_image=Image.open('./saves/좌표2.png'),width=800,key="canvas2")
with col4:
    st.write('y=ax+b에서 a와 b를<br>입력하세요', unsafe_allow_html=True)
    a2=st.number_input('a', min_value=-5.0, max_value=5.0, step=0.5,key='a2')
    b2=st.number_input('b',min_value=-10.0, max_value=10.0, step=0.5,key='b2')
    st.write(f'y={a2}x+{b2}')
    button2=st.button('확인하기',key='button2')
    if button2:
        if a2==1 and b2==1:
            st.write('맞아요! 수직이등분선을 잘 구했습니다')
            st.session_state['answer1']+=1
        else:
            st.write('다시 확인해봅시다. <br>두 직선이 수직일 때 <br>두 직선의 기울기의 곱이 -1 이었죠?', unsafe_allow_html=True)

st.divider()
if st.session_state['answer1']>0:
    st.write('이제 대기오염 측정소를 기준으로 수직이등분선을 이용하여 보로노이 다이어그램을 그려볼까요?')
