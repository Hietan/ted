import pydot
from zss import Node, simple_distance

def dot_to_tree(path, virtual_root_label="__root__"):
    """DOT → zss.Node。木でないときは仮のルートを追加して扱えるようにする"""
    graphs = pydot.graph_from_dot_file(path, encoding="utf-8")
    g = graphs[0]

    # ノード ID → label 属性
    id_to_label = {}
    for n in g.get_nodes():
        nid = n.get_name().strip('"')
        if nid in ('node',):
            continue
        attrs = n.get_attributes()
        lbl = attrs.get('label', nid).strip('"')
        id_to_label[nid] = lbl

    # エッジから親子リスト構築
    children = {}
    indeg = set()
    all_nodes = set(id_to_label.keys())
    for e in g.get_edges():
        src = e.get_source().strip('"')
        dst = e.get_destination().strip('"')
        children.setdefault(src, []).append(dst)
        indeg.add(dst)

    # トップレベル（入次数 0）のノード一覧
    roots = [nid for nid in all_nodes if nid not in indeg]

    # 仮ルートが必要ならルートリストをその子にする
    if len(roots) != 1:
        virtual_id = "__virtual_root__"
        # 仮ルートのラベル登録
        id_to_label[virtual_id] = virtual_root_label
        # 仮ルートの子リストとして roots を設定
        children[virtual_id] = roots
        root_id = virtual_id
    else:
        root_id = roots[0]

    # 子を ID 昇順で再帰構築
    def build(nid):
        lbl = id_to_label.get(nid, nid)
        node = Node(lbl)
        for cid in sorted(children.get(nid, []), key=lambda x: int(x) if x.isdigit() else x):
            node.addkid(build(cid))
        return node

    return build(root_id)


# 使い方例
t1 = dot_to_tree("poldam-pre.dot")
t2 = dot_to_tree("poldam-breaking.dot")

dist, ops = simple_distance(t1, t2, return_operations=True)
print("Tree Edit Distance:", dist)
for op in ops:
    print(op)
