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

st.header("두 응급실을 기준으로 영역을 나눠보자!")
st.write("두 응급실이 아래와 같이 좌표평면에 (0,0)과 (2,0) 위치에 있을 때, 영역을 나눌 기준선을 그려보세요.")
if 'drawline' not in st.session_state:
    st.session_state['drawline']=0
canvas_result = st_canvas(drawing_mode='line',update_streamlit=True,stroke_width=10,background_image=Image.open('./saves/좌표.png'))
if canvas_result.json_data is not None:
    objects = pd.json_normalize(canvas_result.json_data["objects"]) # need to convert obj to str because PyArrow
    for col in objects.select_dtypes(include=['object']).columns:
        objects[col] = objects[col].astype("str")
    #st.dataframe(objects)
    if len(objects)>0:
        if 270 < int(objects['left'].iloc[-1]) < 320 and objects['width'].iloc[-1] < 7 and objects['height'].iloc[-1] > 350:
            st.write('잘했어요!')
            an=st.selectbox('두 점을 이은 선분의 무엇과 같나요?', options=['평행선','수직이등분선','외심','내심','무게중심'])
            if an=='수직이등분선':
                
                st.write('맞아요! 응급실을 이은 선분의 수직이등분선이 영역을 나누는 기준선이 됩니다.')
            
        else:
            st.write('다시 그려 봅시다')
st.divider()

