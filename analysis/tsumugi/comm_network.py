import csv
import re

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def colorize(graph, node_name, node_color: str, font_color: str = 'black') -> None:
    """ノードの色つけを行う関数.

    Args:
        graph (nx.Graph): グラフ
        node_name (hashable): ノード名
        node_color (str): ノードにつけたい色
        font_color (str, optional): ラベルの色. Defaults to 'black'.
    """
    graph.nodes[node_name]['color'] = node_color
    graph.nodes[node_name]['styled'] = 'filled'
    graph.nodes[node_name]['fillcolor'] = node_color
    graph.nodes[node_name]['fontcolor'] = font_color


if __name__ == '__main__':
    # 1人目がメインキャラクターであるcsvの読み込み
    with open('data/comm_characters.csv', 'r') as f:
        reader = csv.reader(f)
        rows = [row for row in reader]

    G = nx.Graph()  # 無向グラフ，有向はDiGraph

    # アイドルのノードを作成
    characters = list(set(sum(rows, [])))  # 一意なアイドルリスト
    for character in characters:
        # 全体曲の列は除外，全体曲は英単語から始まるので正規表現でマッチング
        if re.match('[a-zA-Z]', character):
            continue
        else:
            G.add_node(character)

    # アイドルのエッジリストを作成
    edges = []
    for row in rows:
        # 全体曲の列は除外，全体曲は英単語から始まるので正規表現でマッチング
        if re.match('[a-zA-Z]', row[0]):
            continue
        else:
            # センターと共演のアイドルに分ける
            center, co_stars = row[0], row[1:]
            # print(f'center: {center}, co-stars: {co_stars}')
            for co_star in co_stars:
                edges.append((center, co_star))
            # break

    # アイドルのエッジを作成
    for node_a, node_b in edges:
        # 既にエッジが存在する場合はエッジの重みを増加させる
        if G.has_edge(node_a, node_b):
            G.edges[node_a, node_b]['weight'] += 1
        else:
            G.add_edge(node_a, node_b, weight=1)

    print(G.edges['春日未来', '天海春香'])  # weight=2
    print(G.edges['春日未来', '最上静香'])  # weight=4
    # colorize(G, '春日未来', 'red')
    # colorize(G, '最上静香', 'blue')
    # colorize(G, '伊吹翼', 'yellow')

    # 枝刈り，同時出演回数が一回のみのものは除外
    for (u, v, d) in list(G.edges(data=True)):
        if d['weight'] <= 1:
            G.remove_edge(u, v)
    # # エッジがなくなったノードを削除
    # for character in characters:
    #     if re.match('[a-zA-Z]', character):
    #         continue
    #     else:
    #         if len(list(nx.all_neighbors(G, character))) == 0:
    #             G.remove_node(character)

    # ノード間の反発力とエッジのweightの大きさによる吸引力でノードの位置が決定kが大きいほど円形に
    pos = nx.spring_layout(G, k=0.3)

    # # エッジの太さ調整
    # edge_width = [d['weight'] * 0.2 for (u, v, d) in G.edges(data=True)]
    # nx.draw_networkx_edges(G, pos, alpha=0.4, edge_color='c', width=edge_width)
    # plt.axis('off')
    # plt.show()

    # 基本的な情報を出力
    print(nx.info(G))
    # print('Tsumugi\'s neighbors: ', list(nx.all_neighbors(G, '白石紬')))

    # クラスタリング係数
    clustering_coef = nx.average_clustering(G)

    # 次数中心性(degree)．より多くのノードに接続している人ほど高スコア
    degrees = nx.degree_centrality(G)
    degrees = sorted(degrees.items(), key=lambda x: x[1], reverse=True)

    # 近接中心性(Closeness)，全ての人と近い人が高スコア
    closeness = nx.closeness_centrality(G)
    closeness = sorted(closeness.items(), key=lambda x: x[1], reverse=True)

    # 媒介中心性(Betweenness)．あるノードが他のノードの最短経路に含まれる度合い．様々なコミュニティに所属している人ほど高スコア
    betweenness = nx.betweenness_centrality(G)
    betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)

    # 固有ベクトル中心性(Eigenvector centrality)，隣接するノードの中心性を加味する，他のポピュラーなノード中でポピュラーなものが高スコア
    eigenvectors = nx.eigenvector_centrality(G)
    eigenvectors = sorted(eigenvectors.items(), key=lambda x: x[1], reverse=True)

    print(f'Clustering coefficient: {clustering_coef}')  # クラスタ係数
    print(f'より多くの人と関わりを持っているアイドル:{degrees[:3]}')
    print(f'全ての人と近いアイドル:{closeness[:3]}')
    print(f'様々なコミュニティに所属しているアイドル:{betweenness[:3]}')
    print(f'最もポピュラーなアイドル:{eigenvectors[:3]}')

    # 可視化
    nx.nx_agraph.view_pygraphviz(G, prog='fdp')

    # 度数分布をプロット
    plt.bar(range(len(nx.degree_histogram(G))), height=nx.degree_histogram(G))
    plt.title('Degree histgram')
    plt.xlabel('Number of degrees')
    plt.ylabel('Count')
    plt.xticks(np.arange(0, len(nx.degree_histogram(G)), 1))
    plt.show()
