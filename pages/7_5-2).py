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

@st.cache_resource
def create_map_with_voronoi(points, new_point=None):
    m = folium.Map(location=[37.6456143, 127.0737463], zoom_start=12)
    
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

# 초기 포인트 설정
points = df[df['주소'].str.contains('노원')][['병원위도', '병원경도']].to_numpy()

st.header('노원구 응급실로 그린 보로노이 다이어그램')
st.subheader('만약 노원구에 새로운 응급실을 만들 수 있다면 어디에 세워야 가장 효과적일까요?')
st.subheader('새로운 응급실 위치를 정해봅시다.')

col1, col2 = st.columns([1, 20])
with col1:
    st.image('./saves/marker.png')
with col2:
    st.write(' 를 눌러 새로운 응급실의 위치를 정하고 면적 등을 고려하여 최적의 위치를 정해보세요!')

# 디버그 정보 표시
st.write("Debug: Creating initial map")

# 지도 생성 및 표시
map_obj = create_map_with_voronoi(points)
st.write("Debug: Map object created")

try:
    folium_static(map_obj, width=800, height=600)
    st.write("Debug: Map displayed successfully")
except Exception as e:
    st.error(f"Error displaying map: {str(e)}")

# 새로운 좌표 처리를 위한 placeholder
new_location_placeholder = st.empty()

# 실행 버튼 추가
if st.button('분석 실행'):
    st.write("Debug: Analysis button clicked")
    new_location = new_location_placeholder.text_input("새로운 측정소의 위도,경도를 입력하세요 (예: 37.6456143,127.0737463)")
    
    if new_location:
        try:
            lat, lon = map(float, new_location.split(','))
            st.write(f"Debug: New location parsed - Lat: {lat}, Lon: {lon}")

            # 새로운 측정소를 포함한 Voronoi 다이어그램 계산 및 시각화
            updated_map = create_map_with_voronoi(points, [lat, lon])
            st.write("Debug: Updated map created")
            
            folium_static(updated_map, width=800, height=600)
            st.write("Debug: Updated map displayed")

            # 면적 계산 및 결과 표시
            new_point = [lat, lon]
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
            newdf_polygons.set_index('측정소명', inplace=True)
            
            # 결과 표시
            t1, t2 = st.tabs(['전체데이터', '면적'])
            
            with t1:
                st.dataframe(newdf_polygons[['면적']], width=600)
                st.write('새로운 측정소의 좌표:', lat, lon)

            with t2:
                col1, col2 = st.columns([3,1])
                with col1:
                    st.bar_chart(data=newdf_polygons['면적'])
                    
                with col2:
                    m1 = newdf_polygons['면적'].mean()
                    s1 = newdf_polygons['면적'].std()
                    st.write(f'면적의 평균: {m1:.2f}')
                    st.write(f'면적의 표준편차: {s1:.2f}')
        except Exception as e:
            st.error(f"Error processing new location: {str(e)}")
    else:
        st.warning("새로운 측정소의 위치를 입력해주세요.")

st.write("Debug: End of script")
