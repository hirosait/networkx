# -*- coding:utf-8 -*-

from math import radians, cos, sin, asin, sqrt, ceil
import os

import folium
import networkx as nx
import numpy as np
import pyproj


from MRD.mrd_package.mrd.Data import Data
# python -m pip install  pyproj-1.9.5.1-cp37-cp37m-win_amd64.whl


#  球面三角形による二点間の距離を計算
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371* c  # 地球の半径 6371km
    return km


if __name__ == "__main__":

    center = 35.440374, 139.4866845
    distance = 10.0  # km

    data_dir = os.path.normpath(r"C:\Users\hiroki\PycharmProjects\mrd\MRD\data")
    d = Data()
    d.set_area(center, distance)
    d.set_path(data_dir)
    d.load()

    # 有向グラフ作成
    G = nx.DiGraph()

    # ノードを追加
    for node in d.road.all_node.keys():
        G.add_node(node)

    # エッジを追加
    piece_length = []
    for k, v, in d.road.all_way.items():
        for i in range(len(v.link)):
            if i == len(v.link) - 1:
                break
            lat_1, lon_1 = v.link[i]
            lat_2, lon_2 = v.link[i+1]
            dist = haversine(lon_1, lat_1, lon_2, lat_2)
            piece_length.append(dist)

        # 一方通行規制　正方向のみ
        if v.link_kisei in (4, 6):
            G.add_edge(k[0], k[1], weight=v.link_length, link=v.link, piece_length=piece_length)
        # 一方通行規制　逆方向のみ
        elif v.link_kisei in (5, 7):
            G.add_edge(k[1], k[0], weight=v.link_length, link=v.link[::-1], piece_length=piece_length[::-1])
        # 規制なし 双方向
        else:
            G.add_edge(k[0], k[1], weight=v.link_length, link=v.link, piece_length=piece_length)
            G.add_edge(k[1], k[0], weight=v.link_length, link=v.link[::-1], piece_length=piece_length[::-1])

    print(nx.info(G))
    nx.write_gpickle(G, 'yamato.pickle')

# # 地図
# map_ = folium.Map(location=[center[0], center[1]], zoom_start=18, control_scale=True, prefer_canvas=True)
# for k, v in d.road.all_way.items():
#     reverse = False
#     if v.link_kisei in [4,5,6,7,8]:
#         link_length = "length: {}m".format(str(v.link_length))
#         if v.link_kisei in [5, 7]:
#             reverse = True
#         arrows = get_arrows(locations=v.link, reverse=reverse)
#         for arrow in arrows:
#             arrow.add_to(map_)
#         folium.PolyLine(locations=v.link, tooltip=link_length, color="red", weight="4.5", opacity=0.6).add_to(map_)
#
# map_.save('my_map.html')
