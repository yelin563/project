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
        radius = np.ptp(vor.points, axis=0).max()

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
map = st_folium(initial_map, width=800)
   
