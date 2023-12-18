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
from streamlit_gsheets import GSheetsConnection

st.set_page_config(layout="wide")

if 'name' not in st.session_state:
    st.session_state['name']='N'

num=st.text_input('학번이름을 입력해주세요 ex)21246윤예린')
if num is not None:
    st.write(f"학번이 {num}(으)로 제출되었습니다. ")
    st.session_state['name']=num
st.title("환경탐험가 모드 ON: 대기오염 속으로")
st.write(r'''<span style="font-size: 20px;">$\textsf{[학습목표] 대기오염 측정소의 역할을 살펴보고 각 위치의 대기오염 정도를 결정해보자.}$</span>''', unsafe_allow_html=True)


st.video('https://www.youtube.com/watch?v=MpAB0-g0k4k', format="video/mp4", start_time=0)

st.divider()

st.subheader("대기오염 측정소")
st.write(r'''<span style="font-size: 20px;">$\textsf{서울의 미세먼지 측정소를 클릭하여 현재 무엇을 측정하고 있는지 살펴봅시다}$</span>''', unsafe_allow_html=True)

df=pd.read_csv("./saves/미세먼지측정소_서울.csv")
m = folium.Map([37.55, 127], zoom_start=11)

url=f'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty?sidoName=서울&pageNo=1&numOfRows=100&returnType=json&serviceKey={st.secrets["airkoreaapi"]}&ver=1.5'
response = requests.get(url)
items_list=response.json()["response"]["body"]["items"]
rdf = json_normalize(items_list)

df.apply(lambda row:Marker(location=[row["dmX"],row["dmY"]],icon=folium.Icon(color='green'),
                            popup=row['stationName']).add_to(m),axis=1)

map=st_folium(m,width=725,height=400)
name=map['last_object_clicked_popup']
if name:
    st.write(f'현재 {name} 측정소에서 측정하고 있는 데이터')
    
    st.dataframe(rdf[rdf['stationName']==name].transpose().dropna(),width=725)

st.divider()
st.write(r'''$\textsf{\Large 각 데이터가 무엇을 의미할까요?}$''')
tab1, tab2, tab3, tab4, tab5, tab6, tab7,tab8 = st.tabs(["so2",'co','no2','o3','pm10','pm2.5','khai','기타'])
with tab1:
    st.subheader("이황산가스 SO2")
    st.write("물에 잘 녹는 무색의 자극적인 냄새가 나는 불연성 가스입니다. ")
    st.write(" 황을 함유하는 석탄, 석유 등의 화석연료가 연소될 때 인위적으로 배출되며, 주요 배출원은 발전소, 난방장치, 금속 제련공장, 정유공장 및 기타 산업공정 등에서 발생합니다.")
    st.write("고농도의 아황산가스는 옥외 활동이 많고 천식에 걸린 어른과 어린이에게 일시적으로 호흡장애를 일으킬 수 있으며, 고농도에 폭로될 경우 호흡기계 질환을 일으키고 심장혈관 질환을 악화시키는 것으로 알려져 있습니다. ")
    st.write("산성비의 주요원인 물질로 토양등의 산성화에 영향을 미치고 바람에 의해 장거리 수송되어 다른 지역에 영향을 주며 식물의 잎맥손상 등을 일으키고 시정장애를 일으키며 각종 구조물의 부식을 촉진시킵니다.")
    st.write("so2value는 아황산가스 농도(단위 : ppm)를 나타내며 so2Grade는 아황산가스 지수를 나타냅니다.")
    st.write("지수에서 1은 좋음, 2는 보통, 3은 나쁨, 4는 매우 나쁨을 뜻합니다. ")
with tab2:
    st.subheader("일산화탄소 CO")
    st.write("일산화탄소는 무색, 무취의 유독성 가스로서 연료속의 탄소성분이 불완전 연소되었을 때 발생합니다. ")
    st.write("주로 차에서 나오며, 산업공정과 연료연소 그리고 산불과 같은 자연발생원 및 주방, 담배연기, 지역난방과 같은 실내 발생원이 있다.")
    st.write("일산화탄소의 인체 영향을 살펴보면, 혈액순환 중에서 산소운반 역할을 하는 헤모글로빈을 카르복실헤모글로빈(COHb)으로 변성시켜 산소의 운반기능을 저하시키며, 고농도의 일산화탄소는 유독성이 있어 건강한 사람에게도 치명적인 해를 입힙니다.")
    st.write("coValue는 일산화탄소 농도(단위 : ppm)를 나타내며 coGrade는 일산화탄소 지수를 나타냅니다.")
    st.write("지수에서 1은 좋음, 2는 보통, 3은 나쁨, 4는 매우 나쁨을 뜻합니다. ")
with tab3:
    st.subheader("이산화질소 NO2")
    st.write("이산화질소는 적갈색의 반응성이 큰 기체로서, 오존을 생성하는 역할을 합니다.")
    st.write("주요 배출원은 자동차, 발전소며, 토양중의 세균에 의해 생성되는 자연적 현상 등이 있습니다.")
    st.write("고농도에 노출되면 눈, 코 등의 점막에서 만성 기관지염, 폐렴, 폐출혈, 폐수종의 발병으로까지 발전할 수 있는 것으로 보고되고 있으며, 식물에 대한 피해로는 식물세포를 파괴하여 꽃식물의 잎에 갈색이나 흑갈색의 반점이 생기게 합니다.")
    st.write("no2Value는 이산화질소 농도(단위 : ppm)를 나타내며 no2Grade는 이산화질소 지수를 나타냅니다.")
    st.write("지수에서 1은 좋음, 2는 보통, 3은 나쁨, 4는 매우 나쁨을 뜻합니다. ")
with tab4:
    st.subheader("오존 O3")
    st.write("오존은 대기 중에 배출된 화학물질이 자외선과 광화학 반응을 일으켜 생성된 2차 오염물질에 속합니다. ")
    st.write("자동차, 화학공장, 정유공장과 같은 산업시설과 자연적 생성 등 다양한 배출원에서 발생합니다.")
    st.write("오존에 반복 노출시에는 폐에 피해를 줄 수 있는데, 가슴의 통증, 기침, 메스꺼움, 목 자극, 소화 등에 영향을 미치며, 기관지염, 심장질환, 폐기종 및 천식을 악화시키고, 폐활량을 감소 시킬 수 있습니다. ")
    st.write("특히 기관지 천식환자나 호흡기 질환자, 어린이, 노약자 등에게는 많은 영향을 미치므로 주의해야 할 필요가 있습니다. 또한 농작물과 식물에 직접적으로 영향을 미쳐 수확량이 감소되기도 하며 잎이 말라 죽기도 합니다.")
    st.write("o3Value는 오존 농도(단위 : ppm)를 나타내며 o3Grade는 오존 지수를 나타냅니다.")
    st.write("지수에서 1은 좋음, 2는 보통, 3은 나쁨, 4는 매우 나쁨을 뜻합니다. ")
with tab5:
    st.subheader("미세먼지")
    st.write("미세먼지는 직경에 따라 PM-10과 PM-2.5등으로 구분하며, PM-10은 1000분의 10mm보다 작은 먼지를 말합니다.")
    st.write("사업장 연소, 자동차 연료 연소, 생물성 연소 과정등 특정 배출원으로부터 직접 발생합니다.")
    st.write("천식과 같은 호흡기계 질병을 악화시키고, 폐 기능의 저하를 초래합니다. 또한 미세먼지는 시정을 악화시키고, 식물의 잎 표면에 침적되어 신진대사를 방해하며, 건축물이나 유적물 및 동상 등에 퇴적되어 부식을 일으킵니다.")
    st.write("pm10Value는 미세먼지(PM10) 농도 (단위 : ㎍/㎥)를 나타내며 pm10Grade는 미세먼지(PM10) 24시간 등급을 나타냅니다.")
    st.write("pm10Value24는 미세먼지(PM10) 24시간예측 이동농도(단위 : ㎍/㎥)를 나타내며 pm10Grade1h는 미세먼지(PM10) 1시간 등급을 나타냅니다.")
    st.write("등급에서 1은 좋음, 2는 보통, 3은 나쁨, 4는 매우 나쁨을 뜻합니다. ")
with tab6:
    st.subheader("초미세먼지")
    st.write("미세먼지는 직경에 따라 PM-10과 PM-2.5등으로 구분하며, PM-2.5는1000분의 2.5mm보다 작은 먼지로, 머리카락 직경(약 60㎛)의 1/20~1/30 크기보다 작은 입자입니다. ")
    st.write("사업장 연소, 자동차 연료 연소, 생물성 연소 과정등 특정 배출원으로부터 직접 발생하기도 하지만 PM-2.5의 경우 상당량이 전구물질이 대기 중의 특정 조건에서 반응하여 2차 생성됩니다. ")
    st.write("PM-2.5는 입자가 미세하여 코 점막을 통해 걸러지지 않고 흡입시 폐포까지 직접 침투하여 천식이나 폐질환의 유병률과 조기사망률을 증가시킵니다. ")
    st.write("pm25Value는 미세먼지(PM2.5) 농도 (단위 : ㎍/㎥)를 나타내며 pm25Grade는 미세먼지(PM2.5) 24시간 등급을 나타냅니다.")
    st.write("pm25Value24는 미세먼지(PM2.5) 24시간예측 이동농도(단위 : ㎍/㎥)를 나타내며 pm25Grade1h는 미세먼지(PM2.5) 1시간 등급을 나타냅니다.")
    st.write("등급에서 1은 좋음, 2는 보통, 3은 나쁨, 4는 매우 나쁨을 뜻합니다. ")
with tab7:
    st.subheader("통합대기환경지수")
    st.write("통합대기환경지수(CAI, Comprehensive air-quality index)는 대기오염도 측정치를 국민이 쉽게 알 수 있도록 하고 대기오염으로부터 피해를 예방하기 위한 행동지침을 국민에게 제시하기 위하여 대기오염도에 따른 인체 영향 및 체감오염도를 고려하여 개발된 대기오염도 표현방식입니다.")
    st.write("khaiValue는 통합대기환경 점수를 뜻하며 0에서 500까지의 점수가 커질수록 대기상태가 좋지 않음을 나타냅니다.")  
    st.write("khaiGrade는 통합대기환경 점수를 4단계로 나누어 1은 좋음, 2는 보통, 3은 나쁨, 4는 매우 나쁨을 뜻합니다.")      
with tab8:
    st.write("~Flag는 측정자료 상태정보(점검및교정,장비점검,자료이상,통신장애)를 알려줍니다.")    
    st.write("dataTime은 오염도를 측정한 시간 (연-월-일 시간 : 분)을 나타냅니다.")
    st.write("stationName은 측정소 이름, stationCode는 측정소 코드를 나타냅니다.")
    st.write("mangName은 측정망 정보 (도시대기, 도로변대기, 국가배경농도, 교외대기, 항만)를 뜻합니다.")
  
st.divider()

res1=st.text_area("대기오염 측정소에서 측정하고 있는 데이터를 통해 알게 된 사실을 한 가지이상 적어주세요.")

if st.button('제출하기'):
    if st.session_state['name']=='N':
        st.write('첫 페이지의 위에 학번 이름을 입력해주세요')
    else:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df1 = conn.read(
        worksheet="response1",
        ttl="1s",
        usecols=[0, 1],
        nrows=100
        )  
        df1 = df1.dropna(axis=0)
        st.dataframe(df1) 
        new_data=pd.DataFrame({'학번':st.session_state['name'],'답변':res1},index=[0])
        st.dataframe(new_data) 
        conn.update(worksheet="response1",data=pd.concat([df1, new_data], ignore_index=True))

    
    
    
    
