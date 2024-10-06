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
st.header(" 을지대학교 병원으로 가야 하는 위치는?")



@st.cache_data
def load_data():
    
    df = pd.read_csv("./saves/서울시 응급실 위치 정보.csv", encoding='cp949')
    return df

df = load_data()


m = folium.Map([37.6456143,127.0737463], zoom_start=14)

Marker([37.6468287, 127.072828],popup='중계롯데우성아파트',icon=folium.Icon(color='blue',icon='star')).add_to(m)
Marker([37.6467375, 127.0709664],popup='롯데마트',icon=folium.Icon(color='blue',icon='star')).add_to(m)
Marker([37.6463141, 127.0753281],popup='주공8단지',icon=folium.Icon(color='blue',icon='star')).add_to(m)
Marker([37.6426865, 127.0737866],popup='주공9단지',icon=folium.Icon(color='blue',icon='star')).add_to(m)
Marker([37.6444465, 127.0719057],popup='하계현대2차',icon=folium.Icon(color='blue',icon='star')).add_to(m)
Marker([37.6456143, 127.0737463],popup='불암중',icon=folium.Icon(color='blue',icon='star')).add_to(m)
df.apply(lambda row:Marker(location=[row["병원위도"],row["병원경도"]],icon=folium.Icon(color='green'),
                            popup= row['기관명']).add_to(m),axis=1)
folium.plugins.Draw(export=False).add_to(m)
folium_static(m)
with st.form("form"):
    
    ms=st.multiselect("을지대병원으로 가야하는 위치를 모두 선택해보세요",options=['중계롯데우성아파트','롯데마트','주공8단지','주공9단지','하계현대2차','불암중'])
    b1=st.form_submit_button("확인하기")
if b1:
    if set(ms)==set(['하계현대2차','주공9단지']):
        st.write("위치를 잘 골랐네요!")
        st.write("하지만 이렇게 각 위치에서 가장 가까운 응급실을 매번 찾는 건 귀찮은 일이에요.")
        st.write("다른 좋은 방법을 생각해봅시다.")
        
    else:
        
        st.write("다시 선택해봅시다")
    
    

    
    

    
