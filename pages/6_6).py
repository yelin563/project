import streamlit as st
import pandas as pd
from PIL import Image
import folium
from folium import Marker
from streamlit_folium import st_folium, folium_static
import matplotlib
import matplotlib.pyplot as plt

from streamlit_gsheets import GSheetsConnection
import requests
from branca.colormap import linear
from scipy.spatial import Voronoi, voronoi_plot_2d
import numpy as np
from shapely.geometry import MultiPoint, Point, Polygon
import geopandas as gpd

st.set_page_config(layout="wide")

def voronoi_finite_polygons_2d(vor, radius=None):
    """
    Reconstruct infinite voronoi regions in a 2D diagram to finite
    regions.

    Parameters
    ----------
    vor : Voronoi
        Input diagram
    radius : float, optional
        Distance to 'points at infinity'.

    Returns
    -------
    regions : list of tuples
        Indices of vertices in each revised Voronoi regions.
    vertices : list of tuples
        Coordinates for revised Voronoi vertices. Same as coordinates
        of input vertices, with 'points at infinity' appended to the
        end.

    """

    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max()

    # Construct a map containing all ridges for a given point
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    # Reconstruct infinite regions
    for p1, region in enumerate(vor.point_region):
        vertices = vor.regions[region]

        if all(v >= 0 for v in vertices):
            # finite region
            new_regions.append(vertices)
            continue

        # reconstruct a non-finite region
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                # finite ridge: already in the region
                continue

            # Compute the missing endpoint of an infinite ridge

            t = vor.points[p2] - vor.points[p1] # tangent
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal

            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius

            new_region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())

        # sort region counterclockwise
        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:,1] - c[1], vs[:,0] - c[0])
        new_region = np.array(new_region)[np.argsort(angles)]

        # finish
        new_regions.append(new_region.tolist())

    return new_regions, np.asarray(new_vertices)

sido = gpd.read_file('./ctprvn_20230729/ctprvn.shp', encoding='cp949')
sido.crs = "EPSG:5179"
sido['center_point'] = sido['geometry'].geometry.centroid
sido['geometry'] = sido['geometry'].to_crs(epsg=4326)
sido['center_point'] = sido['center_point'].to_crs(epsg=4326)
sido['경도'] = sido['center_point'].map(lambda x: x.xy[0][0])
sido['위도'] = sido['center_point'].map(lambda x: x.xy[1][0])
exterior_coords = list(sido['geometry'][0].exterior.coords)
new_coords = [(y, x) for x, y in exterior_coords]
seoul_poly = Polygon(new_coords)
df1=pd.read_csv("./saves/22_미세먼지_월별.csv")

df=pd.read_csv("./saves/미세먼지측정소_서울.csv")

st.header('측정소로 그린 보로노이 다이어그램')
st.subheader('만약 새로운 측정소를 만들 수 있다면 어디에 세워야 가장 효과적일까요?')
st.subheader('새로운 측정소 위치를 정해봅시다.')
col1,col2=st.columns([1,20])
with col1:
    st.image('./saves/marker.png')
with col2:
    st.write(' 를 눌러 새로운 측정소의 위치를 정하고 면적과 연평균을 고려하여 최적의 위치를 정해보세요!')

m = folium.Map([37.55, 127], zoom_start=11)



points=df[['dmX', 'dmY']].to_numpy()
points= points.astype(float)
vor = Voronoi(points)
regions, vertices = voronoi_finite_polygons_2d(vor)
temp=[]


for region in regions:
    polygon = vertices[region]
    temp.append(polygon)





data_list = []

colormap = linear.viridis.scale(-df1['연평균'].max(),-df1['연평균'].min())
for i, region in enumerate(regions):
    polygon = vertices[region]
    p1 = Polygon(polygon)
    p = seoul_poly.intersection(p1)
    mean=df1[df['stationName'][i]==df1['측정소명']]['연평균'].values[0]
    if p.type == 'MultiPolygon':
        temp=0
        for poly in p.geoms:
                       
            polygon_coords = poly.exterior.coords
            polygon_area = poly.area
            temp+=polygon_area
                
            folium.Polygon(locations=polygon_coords, color='black',fill_color=colormap(-mean), fill=True, fill_opacity=0.7).add_to(m)
        data_list.append({'Region': region, '면적': temp})
    else:
        
        polygon_coords = p.exterior.coords
        polygon_area = p.area
        
        data_list.append({'Region': region, '면적': polygon_area})
        
        folium.Polygon(locations=polygon_coords, color='black',fill_color=colormap(-mean), fill=True, fill_opacity=0.7).add_to(m)

df_polygons = pd.DataFrame(data_list)
df_polygons['측정소명']=df['stationName']
df_polygons['면적'] = (df_polygons['면적'] * 10014).astype(int)
df_polygons = pd.merge(df_polygons, df1[['측정소명', '연평균']], on='측정소명', how='left')


for i, coord in enumerate(points):
    polygon_info = df_polygons.loc[i, ["측정소명", "면적",'연평균']]
    popup_html = polygon_info.to_frame().to_html(classes="table table-striped table-hover table-condensed table-responsive")
    popup = folium.Popup(popup_html, max_width=300)
    folium.Marker(location=[coord[0], coord[1]], popup=popup,icon=folium.Icon(color='green')).add_to(m)
folium.plugins.Draw(export=False).add_to(m)
col1, col2=st.columns([5,1])
with col1:
    map=st_folium(m,width=800,use_container_width=True)
if map['last_active_drawing'] is not None:
    newcoor=map['last_active_drawing']['geometry']['coordinates']
    with col2:
        
        st.write('새로운 측정소의 좌표')
        st.write(newcoor[1])
        st.write(newcoor[0])
            


if map['last_active_drawing'] is not None:
    
    m1 = folium.Map([37.55, 127], zoom_start=11)
    folium.Marker(location=newcoor, popup='새로운 측정소').add_to(m1)

    new_point = pd.DataFrame({'dmX': [newcoor[1]], 'dmY': [newcoor[0]],"item":'SO2, CO, O3, NO2, PM10, PM2.5', \
        'mangName':'새로운측정소','year':'2023','addr':'서울','stationName':'새로운측정소'})
    newdf = pd.concat([df, new_point], ignore_index=True)
    newpoints=newdf[['dmX', 'dmY']].to_numpy()
    newpoints= newpoints.astype(float)
    newvor = Voronoi(newpoints)
    newregions, newvertices = voronoi_finite_polygons_2d(newvor)


    newdata_list = []

    colormap = linear.viridis.scale(-df1['연평균'].max(),-df1['연평균'].min())
    for i, region in enumerate(newregions):
        polygon = newvertices[region]
        p1 = Polygon(polygon)
        p = seoul_poly.intersection(p1)
        if i<len(newregions)-1:
            
            mean=df1[newdf['stationName'][i]==df1['측정소명']]['연평균'].values[0]
            if p.type == 'MultiPolygon':
                temp=0
                for poly in p.geoms:
                            
                    polygon_coords = poly.exterior.coords
                    polygon_area = poly.area
                    temp+=polygon_area
                        
                    folium.Polygon(locations=polygon_coords, color='black',fill_color=colormap(-mean), fill=True, fill_opacity=0.7).add_to(m1)
                newdata_list.append({'Region': region, '면적': temp})
            else:
                
                polygon_coords = p.exterior.coords
                polygon_area = p.area
                
                newdata_list.append({'Region': region, '면적': polygon_area})
                
                folium.Polygon(locations=polygon_coords, color='black',fill_color=colormap(-mean), fill=True, fill_opacity=0.7).add_to(m1)
        else:
            
            if p.type == 'MultiPolygon':
                temp=0
                for poly in p.geoms:
                            
                    polygon_coords = poly.exterior.coords
                    polygon_area = poly.area
                    temp+=polygon_area
                        
                    folium.Polygon(locations=polygon_coords, color='black',fill_color='red', fill=True, fill_opacity=0.7).add_to(m1)
                newdata_list.append({'Region': region, '면적': temp})
            else:
                
                polygon_coords = p.exterior.coords
                polygon_area = p.area
                
                newdata_list.append({'Region': region, '면적': polygon_area})
                
                folium.Polygon(locations=polygon_coords, color='black',fill_color='red', fill=True, fill_opacity=0.7).add_to(m1)
    new_df = pd.DataFrame({'측정소명':'새로운측정소','측정소코드':'새로운측정소','연평균':'?'}, index=[0])
    for i in range(1, 13):
        new_df[f'{i}월'] = '?'
    newdf1 = pd.concat([df1, new_df], ignore_index=True)

    newdf_polygons = pd.DataFrame(newdata_list)
    newdf_polygons['측정소명']=newdf['stationName']
    newdf_polygons['면적'] = (newdf_polygons['면적'] * 10014).astype(int)
    newdf_polygons = pd.merge(newdf_polygons, newdf1[['측정소명', '연평균']], on='측정소명', how='left')

    for i, coord in enumerate(newpoints):
        polygon_info = newdf_polygons.loc[i, ["측정소명", "면적",'연평균']]
        popup_html = polygon_info.to_frame().to_html(classes="table table-striped table-hover table-condensed table-responsive")
        popup = folium.Popup(popup_html, max_width=300)
        folium.Marker(location=[coord[0], coord[1]], popup=popup).add_to(m1)
    folium_static(m1,width=800)
    
    a=st.number_input('새로운 측정소의 미세먼지 농도를 가상으로 설정하고 면적과 미세먼지 농도 데이터를 분석해봅시다.')
    if a:
        a=float(a)
        t1, t2, t3= st.tabs(['전체데이터','면적','연평균'])
        
        newdf_polygons.loc[newdf_polygons['측정소명']=='새로운측정소', '연평균'] = a
        newdf_polygons.set_index('측정소명', inplace=True)
        with t1:
            st.dataframe(newdf_polygons[['면적','연평균']],width=600)
        with t2:
            col1, col2 = st.columns([3,1])
            with col1:
                st.bar_chart(data=newdf_polygons['면적'])
                
            with col2:
                m1=newdf_polygons['면적'].mean()
                s1=newdf_polygons['면적'].std()
                st.write(f'면적의 평균: {m1:.2f}')
                st.write(f'면적의 표준편차: {s1:.2f}')
        with t3:
            col1, col2 = st.columns([3,1])
            with col1:
                
                st.bar_chart(data=newdf_polygons['연평균'])
            with col2:
                m1=newdf_polygons['연평균'].mean()
                s1=newdf_polygons['연평균'].std()
                st.write(f'연평균의 평균: {m1:.2f}')
                st.write(f'연평균의 표준편차: {s1:.2f}')
        
    
    st.divider()
    res4=st.text_area("새로운 측정소의 위치를 어떻게 정했는지 설명해주세요.")
    
    if st.button('제출하기'):
        if st.session_state['name']=='N':
            st.write('첫 페이지의 위에 학번 이름을 입력해주세요')
        else:
            conn = st.connection("gsheets", type=GSheetsConnection)
            rdf4 = conn.read(
            worksheet="response4",
            ttl="1s",
            usecols=[0, 1,2,3],
            nrows=100
            )  
            rdf4 = rdf4.dropna(axis=0)
            st.dataframe(rdf4) 
            new_data=pd.DataFrame({'학번':st.session_state['name'],'답변':res4,'위도':newcoor[1],'경도':newcoor[0]},index=[0])
            
            conn.update(worksheet="response4",data=pd.concat([rdf4, new_data], ignore_index=True))   

        
