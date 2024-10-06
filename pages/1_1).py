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

st.subheader("1.주변 응급실 살펴보기")
st.write("주변 응급실을 살펴보고 새로 알게 된 점 혹은 느낀 점을 학습지에 적어주세요.")


@st.cache_data
def load_data():
    
    df = pd.read_csv("./saves/서울시 응급실 위치 정보.csv", encoding='cp949')
    return df

df = load_data()

sch_loc=[37.6456143, 127.0737463]
m = folium.Map(sch_loc, zoom_start=13)


df.apply(lambda row:Marker(location=[row["병원위도"],row["병원경도"]],icon=folium.Icon(color='green'),
                            popup= row['기관명']).add_to(m),axis=1)

map=st_folium(m,width=725,height=400)
col = df.pop('기관명')  # 'D' 열을 제거하고 저장
df.insert(1, '기관명', col)
st.dataframe(df.drop(columns=['응급실운영여부','병원분류','기관ID','응급의료기관코드','응급의료기관코드명']))
        
