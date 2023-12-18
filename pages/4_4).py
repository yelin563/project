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

st.header("두 측정소를 기준으로 영역을 나눠보자!")
st.write("두 측정소가 아래와 같이 좌표평면에 (0,0)과 (2,0) 위치에 있을 때, 영역을 나눌 기준선을 그려보세요.")
if 'drawline' not in st.session_state:
    st.session_state['drawline']=0
canvas_result = st_canvas(drawing_mode='line',update_streamlit=True,stroke_width=10,background_image=Image.open('./saves/좌표.png'))
if canvas_result.json_data is not None:
    objects = pd.json_normalize(canvas_result.json_data["objects"]) # need to convert obj to str because PyArrow
    for col in objects.select_dtypes(include=['object']).columns:
        objects[col] = objects[col].astype("str")
    st.dataframe(objects)
    if len(objects)>0:
        if 270 < int(objects['left'].iloc[-1]) < 320 and objects['width'].iloc[-1] < 7 and objects['height'].iloc[-1] > 350:
            st.write('잘했어요!')
            an=st.selectbox('두 점을 이은 선분의 무엇과 같나요?', options=['평행선','수직이등분선','외심','내심','무게중심'])
            if an=='수직이등분선':
                
                st.write('맞아요! 측정소를 이은 선분의 수직이등분선이 영역을 나누는 기준선이 됩니다.')
            
        else:
            st.write('다시 그려 봅시다')
st.divider()
st.header("세 측정소를 기준으로 영역을 나눠보자!")   
st.write("세 측정소가 아래와 같이 점 A,B,C에 있을 때, 영역을 나눌 기준선을 그려보세요.")
st.write("(1) A와 B사이, (2) B와 C사이, (3) C와 A 사이 순서로 그려주세요 ")


canvas_res = st_canvas(drawing_mode='line',update_streamlit=True,stroke_width=10,background_image=Image.open('./saves/좌표1.png'))
if canvas_res.json_data is not None:
    obj = pd.json_normalize(canvas_res.json_data["objects"]) # need to convert obj to str because PyArrow
    for c in obj.select_dtypes(include=['object']).columns:
        obj[c] = obj[c].astype("str")
    st.dataframe(obj)
    if len(obj)>0:
        if 160 < obj['top'].iloc[0] < 200 and obj['left'].iloc[0] < 200  and obj['height'].iloc[0] < 7 and 240<obj['width'].iloc[0] < 300 : 
            st.write('A와 B 사이의 기준선을 잘 나타냈습니다! 이제 B와 C 사이의 기준선을 그려주세요.')
            if len(obj)>1:
                if 250 < obj['top'].iloc[1] < 300 and 250<obj['left'].iloc[1] < 320  and obj['width'].iloc[1]< 7 and 200<obj['height'].iloc[1] :
                    st.write('B와 C 사이의 기준선을 잘 나타냈습니다! 이제 C와 A 사이의 기준선을 그려주세요')
                    if len(obj)>2:
                        if 60 < obj['top'].iloc[2] < 110 and 300<obj['left'].iloc[2] <390  and 120<obj['width'].iloc[2]< 180 and 160<obj['height'].iloc[2]<220 :
                            st.session_state['drawline']+=1
                            st.write('영역을 모두 잘 나눴네요!')
                            if st.session_state['drawline']==1:
                                st.balloons()
                        else:
                            st.write('C와 A 사이의 선을 다시 그려 봅시다.')
                
                else:
                    st.write('B와 C 사이의 선을 다시 그려 봅시다.')
                
        else:
            st.write('다시 그려 봅시다. (1) A와 B사이 부터 그리는 것을 잊지 마세요!')
