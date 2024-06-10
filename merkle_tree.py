import hashlib

class Node:
    def __init__(self, data = None, left_node = None, right_node = None):
        self.left_node = left_node
        self.right_node = right_node
        self.hash = self.hash_node(data)

    def hash_node(self, data):
        if data is None:
            data_str = self.left_node.hash + self.right_node.hash if (self.left_node and self.right_node) else ""
            return hashlib.sha256(data_str.encode()).hexdigest()
        else:
            return hashlib.sha256(data.encode()).hexdigest()


class Merkle_Tree:
    def __init__(self):
        self.root = None
        self.leaves: list[Node] = []

    def add_Node(self, data):
        node = Node(data)
        self.leaves.append(node)
        self.update()

    def update(self):
        if len(self.leaves) == 0:
            self.root = None
            return

        tree_copy = self.leaves
        while len(tree_copy) > 1:
            if len(tree_copy) % 2 == 1:
                tree_copy.append(Node(self.leaves[-1].hash))
            new_node_lvl = []
            for i in range(0, len(tree_copy), 2):
                new_node = Node(left_node = tree_copy[i], right_node = tree_copy[i + 1])
                new_node_lvl.append(new_node)
            tree_copy = new_node_lvl

        self.root = tree_copy[0]

