import streamlit as st
import pandas as pd
import folium
from folium import Marker
from streamlit_folium import st_folium, folium_static
from scipy.spatial import Voronoi
import numpy as np
from shapely.geometry import Polygon
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


@st.cache_data
def load_data():
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
    
    df = pd.read_csv("./saves/서울시 응급실 위치 정보.csv", encoding='cp949')
    return sido, seoul_poly, df

sido, seoul_poly, df = load_data()

st.header('응급실로 그린 보로노이 다이어그램')
st.write('서울 전체의 응급실 위치로 그린 보로노이 다이어그램을 보고 알게 된 점 혹은 느낀 점을 적어주세요.')


# 초기 맵 생성 및 보로노이 다이어그램 그리기
def create_voronoi_map(points, new_point=None):
    m = folium.Map([37.55, 127], zoom_start=11)
    
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
points = df[['병원위도', '병원경도']].to_numpy().astype(float)

# 초기 맵 표시
initial_map = create_voronoi_map(points)
df.apply(lambda row:Marker(location=[row["병원위도"],row["병원경도"]],icon=folium.Icon(color='green'),
                            popup= row['기관명']).add_to(initial_map),axis=1)
map = st_folium(initial_map, width=800, use_container_width=True)
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

        
