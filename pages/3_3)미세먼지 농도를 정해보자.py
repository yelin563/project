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
st.set_page_config(layout="wide")
st.header("각 위치의 미세먼지 농도를 정해보자")

st.write("각 위치에 따라 매번 계산을 하여 미세먼지 농도를 구하는 것은 힘든 일이겠죠?")


col1, col2, col3, col4,col5=st.columns([3,1,11,1,10])
with col1:
    st.write(r'''<span style="font-size: 16px;">$\textsf{주변 측정소}$</span>''', unsafe_allow_html=True)
with col2:
    st.image('./saves/marker1.png')
with col3:
    st.write(r'''<span style="font-size: 16px;">$\textsf{가 측정한 수치들 중에서 선택하는 방법으로 각 위치}$</span>''', unsafe_allow_html=True)
with col4:
    st.image('./saves/marker2.png')
with col5:
    st.write(r'''<span style="font-size: 16px;">$\textsf{의 미세먼지 농도를 정해봅시다.}$</span>''', unsafe_allow_html=True)

df=pd.read_csv("./saves/미세먼지측정소_서울.csv")


m = folium.Map([37.517,127.03], zoom_start=14)

Marker([37.513,127.04],popup='1',icon=folium.Icon(color='blue',icon='star')).add_to(m)
Marker([37.5165,127.03],popup='2',icon=folium.Icon(color='blue',icon='star')).add_to(m)
Marker([37.5175,127.035],popup='3',icon=folium.Icon(color='blue',icon='star')).add_to(m)
Marker([37.523,127.025],popup='4',icon=folium.Icon(color='blue',icon='star')).add_to(m)
Marker([37.519,127.042],popup='5',icon=folium.Icon(color='blue',icon='star')).add_to(m)
Marker([37.515,127.023],popup='6',icon=folium.Icon(color='blue',icon='star')).add_to(m)
df.apply(lambda row:Marker(location=[row["dmX"],row["dmY"]],icon=folium.Icon(color='green'),
                            popup= row['stationName']).add_to(m),axis=1)
folium.plugins.Draw(export=False).add_to(m)
folium_static(m)
with st.form("form"):
    
    ms=st.multiselect("도산대로에서 측정한 수치를 이용할 위치를 모두 선택해보세요",options=[1,2,3,4,5,6])
    b1=st.form_submit_button("확인하기")
if b1:
    if set(ms)==set([2,4,6]):
        st.write("측정소에 가까운 위치를 잘 골랐네요!")
        st.write("하지만 이렇게 각 위치에서 가장 가까운 측정소를 매번 찾는 건 귀찮은 일이에요.")
        st.write(r'''<span style="font-size: 16px;">$\textsf{그렇다면 측정소에 대해 영역을 미리 나누면 훨씬 편하겠죠?}$</span>''', unsafe_allow_html=True)
        
    else:
        
        st.write("다시 선택해봅시다")
    
    

    
