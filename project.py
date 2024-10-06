#10_schoolmap.py

import streamlit as st
import pandas as pd
from PIL import Image
import folium
from folium import Marker
from streamlit_folium import st_folium, folium_static
from folium.plugins import Search
import requests
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d
import numpy as np
from shapely.geometry import MultiPoint, Point, Polygon
import geopandas as gpd
from pandas import json_normalize


st.set_page_config(layout="wide")

st.write(r'''<span style="font-size: 22px;">$\textsf{불암중학교 영재수업}$</span>''', unsafe_allow_html=True)
st.title("보로노이 다이어그램")

st.write(r'''<span style="font-size: 20px;">$\textsf{[학습목표]}$</span>''', unsafe_allow_html=True)

st.write(r'''<span style="font-size: 18px;">$\textsf{1. 주변 응급실 위치를 살펴보고 각 위치에서 어떤 응급실을 가야 할지 결정할 수 있다. }$</span>''', unsafe_allow_html=True)
st.write(r'''<span style="font-size: 18px;">$\textsf{2. 보로노이 다이어그램의 필요성과 의미에 대해 안다. }$</span>''', unsafe_allow_html=True)
st.write(r'''<span style="font-size: 18px;">$\textsf{3. 어느 위치에 응급실을 추가로 설치해야 좋은지 이유를 들어 결정할 수 있다. }$</span>''', unsafe_allow_html=True)

#st.video('https://www.youtube.com/watch?v=MpAB0-g0k4k', format="video/mp4", start_time=0)

st.divider()


    
    
    
    
