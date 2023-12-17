import streamlit as st
import pandas as pd
from PIL import Image
import folium
from folium import Marker
from streamlit_folium import st_folium, folium_static
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from streamlit_gsheets import GSheetsConnection
import requests
from branca.colormap import linear
from scipy.spatial import Voronoi, voronoi_plot_2d
import numpy as np
from shapely.geometry import MultiPoint, Point, Polygon
import geopandas as gpd

from pandas import json_normalize

st.header("내 위치의 미세먼지 농도는?")

st.write("왼쪽의 도구들을 이용하여 내 위치의 미세먼지 농도를 결정해봅시다")
df=pd.read_csv("./saves/미세먼지측정소_서울.csv")
url=f'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty?sidoName=서울&pageNo=1&numOfRows=100&returnType=json&serviceKey={st.secrets["airkoreaapi"]}&ver=1.5'
response = requests.get(url)
items_list=response.json()["response"]["body"]["items"]
rdf = json_normalize(items_list)
sch_loc=[37.4714269, 126.924733]
m = folium.Map(sch_loc, zoom_start=13)

Marker(sch_loc,popup='우리학교',icon=folium.Icon(color='blue',icon='star')).add_to(m)

df.apply(lambda row:Marker(location=[row["dmX"],row["dmY"]],icon=folium.Icon(color='green'),
                            popup=rdf[rdf['stationName'] == row['stationName']][["stationName","pm10Value"]].to_html(classes="table table-striped table-hover table-condensed table-responsive")).add_to(m),axis=1)
folium.plugins.Draw(export=False).add_to(m)
folium_static(m)
st.write("왼쪽의 도구들을 이용하여 내 위치의 미세먼지 농도를 결정해봅시다")
res3=st.text_area("내 위치의 미세먼지 농도를 몇일까요? 그렇게 정한 이유도 써주세요. ")

if st.button('제출하기'):
    if st.session_state['name']=='N':
        st.write('첫 페이지의 위에 학번 이름을 입력해주세요')
    else:
        conn = st.connection("gsheets", type=GSheetsConnection)
        rdf3 = conn.read(
        worksheet="response3",
        ttl="1s",
        usecols=[0, 1],
        nrows=100
        )  
        rdf3 = rdf3.dropna(axis=0)
        
        new_data=pd.DataFrame({'학번':st.session_state['name'],'답변':res3},index=[0])
        
        conn.update(worksheet="response3",data=pd.concat([rdf3, new_data], ignore_index=True))
