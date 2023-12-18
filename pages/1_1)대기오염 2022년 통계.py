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
st.set_page_config(layout="wide")
st.header("대기오염 2022년 통계")

df1=pd.read_csv("./saves/22_미세먼지_월별.csv")
df2=pd.read_csv("./saves/22_초미세먼지_월별.csv")
df3=pd.read_csv("./saves/22_오존_월별.csv")
df4=pd.read_csv("./saves/22_이산화질소_월별.csv")
df5=pd.read_csv("./saves/22_일산화탄소_월별.csv")


df=pd.read_csv("./saves/미세먼지측정소_서울.csv")

m = folium.Map([37.56, 127], zoom_start=11)
df.apply(lambda row:Marker(location=[row["dmX"],row["dmY"]],icon=folium.Icon(color='green'),
                            popup=row['stationName']).add_to(m),axis=1)

ch_list=['미세먼지', '초미세먼지', '오존', '이산화질소', '일산화탄소']
ch=st.selectbox('어떤 데이터를 볼까요?',options=ch_list)
col_list=[f'{i}월' for i in range(1,13)]
col=st.select_slider('언제 측정한 데이터를 볼까요?',options=col_list)
cdf = globals()[f'df{ch_list.index(ch)+1}']
col1, col2= st.columns([3,1])

colormap = linear.Paired_07.scale(cdf[col_list].min().min(),cdf[col_list].max().max())
colormap.caption = f"{ch} 농도"
colormap.add_to(m)
cdf.apply(lambda row:folium.Circle(location=[df[df['stationName'] == row['측정소명']]["dmX"].values[0],df[df['stationName'] == row['측정소명']]["dmY"].values[0]],
                            popup=row['측정소명'],fill=True,fill_opacity=0.7,color=colormap(row[col]),radius=1000).add_to(m),axis=1)
with col1:
    
    map=st_folium(m,width=725,height=450)
with col2:
    
    st.dataframe(cdf[['측정소명',col]],width=225,height=450)

cdf.set_index('측정소명', inplace=True)    
st.write(f"측정소에 따른 {col}의 연평균 {ch} 농도")
st.line_chart(cdf['연평균'])
monthly_mean = cdf[col_list].mean()
monthly_mean.index = [f'{i}월' for i in range(1,10)]+['_10 월','_11 월','_12 월']
st.write(f"각 월별 {ch} 농도")
st.line_chart(monthly_mean)
st.divider()
res2=st.text_area("대기오염 2022년 통계를 통해 알게 된 사실을 한 가지이상 적어주세요.")
 
if st.button('제출하기'):
    if st.session_state['name']=='N':
        st.write('첫 페이지의 위에 학번 이름을 입력해주세요')
    else:
        conn = st.connection("gsheets", type=GSheetsConnection)
        rdf2 = conn.read(
        worksheet="response2",
        ttl="1s",
        usecols=[0, 1],
        nrows=100
        )  
        rdf2 = rdf2.dropna(axis=0)
        
        new_data=pd.DataFrame({'학번':st.session_state['name'],'답변':res2},index=[0])
        
        conn.update(worksheet="response2",data=pd.concat([rdf2, new_data], ignore_index=True))
