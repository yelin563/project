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

st.subheader("2-1.우리 학교에서 다치면 어떤 응급실을 가야 할까요? ")

@st.cache_data
def load_data():
    
    
    df = pd.read_csv("./saves/서울시 응급실 위치 정보.csv", encoding='cp949')
    return df

df = load_data()

sch_loc=[37.6456143, 127.0737463]
m = folium.Map(sch_loc, zoom_start=13)

Marker(sch_loc,popup='우리학교',icon=folium.Icon(color='blue',icon='star')).add_to(m)



df.apply(lambda row:Marker(location=[row["병원위도"],row["병원경도"]],icon=folium.Icon(color='green'),
                            popup= row['기관명']).add_to(m),axis=1)
folium.plugins.Draw(export=False).add_to(m)
folium_static(m)

st.write("왼쪽의 다양한 도구들을 이용하여 우리 학교에서 다치면 어떤 응급실을 가야 할지 결정해보고 학습지에 적어주세요.")

