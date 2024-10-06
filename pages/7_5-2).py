import streamlit as st
import pandas as pd
from PIL import Image
import folium
from folium import Marker
from streamlit_folium import st_folium, folium_static
import matplotlib
import matplotlib.pyplot as plt
from folium.plugins import Draw

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
        radius = np.ptp(vor.points) 

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


@st.cache_data
def load_data():
    sido = gpd.read_file('./saves/BND_SIGUNGU_PG/desired_geometry.shp', encoding='cp949')
    sido.crs = "EPSG:5186"
    sido['center_point'] = sido['geometry'].geometry.centroid
    sido['geometry'] = sido['geometry'].to_crs(epsg=4326)
    sido['center_point'] = sido['center_point'].to_crs(epsg=4326)
    exterior_coords = list(sido['geometry'][0].exterior.coords)
    new_coords = [(y, x) for x, y in exterior_coords]
    seoul_poly = Polygon(new_coords)
    
    df = pd.read_csv("./saves/서울시 응급실 위치 정보.csv", encoding='cp949')
    return sido, seoul_poly, df

sido, seoul_poly, df = load_data()

st.header('노원구 응급실로 그린 보로노이 다이어그램')
st.subheader('만약 노원구에 새로운 응급실을 만들 수 있다면 어디에 세워야 가장 효과적일까요?')
st.subheader('새로운 응급실 위치를 정해봅시다.')

col1, col2 = st.columns([1, 20])
with col1:
    st.image('./saves/marker.png')
with col2:
    st.write(' 를 눌러 새로운 응급실의 위치를 정하고 면적 등을 고려하여 최적의 위치를 정해보세요!')

# 초기 포인트 설정
points = df[df['주소'].str.contains('노원')][['병원위도', '병원경도']].to_numpy()
# 서울 중심 좌표 설정
seoul_center = [37.6456143, 127.0737463]
def create_map_with_voronoi(points, new_point=None):
    m = folium.Map(location=seoul_center, zoom_start=12)
    
    # Draw 플러그인 추가
    draw = Draw(
        draw_options={
            'polyline': False,
            'rectangle': False,
            'polygon': False,
            'circle': False,
            'circlemarker': False,
            'marker': True,
        },
        edit_options={'edit': False}
    )
    draw.add_to(m)
    
    if new_point is not None:
        points = np.vstack([points, new_point])
    
    vor = Voronoi(points)
    regions, vertices = voronoi_finite_polygons_2d(vor)
    
    for region in regions:
        polygon = vertices[region]
        p1 = Polygon(polygon)
        p = seoul_poly.intersection(p1)
        if not p.is_empty:
            if p.type == 'MultiPolygon':
                for poly in p.geoms:
                    folium.Polygon(locations=poly.exterior.coords, color='blue', fill=True, fill_opacity=0.3).add_to(m)
            else:
                folium.Polygon(locations=p.exterior.coords, color='blue', fill=True, fill_opacity=0.3).add_to(m)
    
    for point in points:
        folium.Marker(location=[point[0], point[1]]).add_to(m)
    
    if new_point is not None:
        folium.Marker(location=new_point, popup='새로운 측정소', icon=folium.Icon(color='red')).add_to(m)
    
    return m

# 초기 지도 생성
initial_map = create_map_with_voronoi(points)
# map_data = st_folium(initial_map, width=800, height=600)
# Streamlit의 session_state를 사용하여 지도 상태를 유지
if 'map' not in st.session_state:
    st.session_state.map = initial_map
if 'run' not in st.session_state:
    st.session_state.run = 'N'
# 지도 표시

# folium 지도 데이터를 st_folium으로 받음
map_data = st_folium(st.session_state.map, width=800, height=600)

# 새로운 좌표를 세션에 저장
if map_data:
    if map_data['last_active_drawing']:
        st.session_state['new_location'] = map_data['last_active_drawing']['geometry']['coordinates']
        st.write('새로운 측정소의 좌표:', st.session_state['new_location'][1], st.session_state['new_location'][0])

# 실행 버튼 추가
if st.button('분석 실행') and 'new_location' in st.session_state:
    # 새로운 측정소를 포함한 Voronoi 다이어그램 계산 및 시각화
    updated_map = create_map_with_voronoi(points, [st.session_state['new_location'][1], st.session_state['new_location'][0]])
    st.session_state.map = updated_map
    st.session_state['run'] = 'Y'
    st.rerun()

# 면적 계산 및 결과 표시
if st.session_state.get('run') == 'Y' and 'new_location' in st.session_state:
    new_point = [st.session_state['new_location'][1], st.session_state['new_location'][0]]
    vor = Voronoi(np.vstack([points, new_point]))
    regions, vertices = voronoi_finite_polygons_2d(vor)
    
    data_list = []
    for i, region in enumerate(regions):
        polygon = vertices[region]
        p1 = Polygon(polygon)
        p = seoul_poly.intersection(p1)
        area = p.area if not p.is_empty else 0
        data_list.append({'측정소명': df['기관명'].iloc[i] if i < len(df) else '새로운측정소', '면적': area * 10014})

    newdf_polygons = pd.DataFrame(data_list)
    newdf_polygons['면적'] = newdf_polygons['면적'].astype(int)
    
    

    # 측정소명을 인덱스로 설정
    newdf_polygons.set_index('측정소명', inplace=True)
    
    # 결과 표시
    t1, t2 = st.tabs(['전체데이터', '면적'])
    
    with t1:
        st.dataframe(newdf_polygons[['면적']], width=600)
        st.write('새로운 측정소의 좌표:', st.session_state['new_location'][1], st.session_state['new_location'][0])

    with t2:
        col1, col2 = st.columns([3,1])
        with col1:
            st.bar_chart(data=newdf_polygons['면적'])
            
        with col2:
            m1 = newdf_polygons['면적'].mean()
            s1 = newdf_polygons['면적'].std()
            st.write(f'면적의 평균: {m1:.2f}')
            st.write(f'면적의 표준편차: {s1:.2f}')
        
