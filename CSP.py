from queue import Queue

class Node:
    """A CSP Node."""

    def __init__(self, key, domain):
        self.key = key
        self.domain: set = domain

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        return self.key == other.key

    def __ne__(self, other):
        return not(self == other)

    def __repr__(self):
        return f"{self.key}"

    def __str__(self):
        return f"{self.key}"

    def __lt__(self, other):
        return self.key < other.key

    def __gt__(self, other):
        return self.key > other.key

class Graph:
    """A CSP Graph."""
    @staticmethod
    def parse_domain(domain_str: str):
        """Parse the separated domain."""
        return set([x.strip() for x in domain_str.split(',')])

    def __init__(self, file_path):
        self.nodes = {}
        self.edges = {}

        with open(file_path, 'r') as file:
            num_nodes = int(file.readline())

            # read the domain of each node
            for _ in range(num_nodes):
                key, rest = [x.strip() for x in file.readline().split(':')]
                # parse domain
                domain = Graph.parse_domain(rest)
                self.nodes[key] = Node(key, domain)
                self.edges[self.nodes[key]] = set()

            for line in file:
                node_a, node_b = [x.strip() for x in line.split('<->')]
                self.edges[self.nodes[node_a]].add(self.nodes[node_b])
                self.edges[self.nodes[node_b]].add(self.nodes[node_a])

    def gen_arcs_queue(self):
        """Convert the self.edges to a frontier queue."""
        sorted_keys = sorted(self.nodes.keys())
        queue = Queue()
        edge_set = {
            (src, dest)
            for src, destinations in self.edges.items()
            for dest in destinations
        }
        for i, key_1 in enumerate(sorted_keys):
            for key_2 in sorted_keys[i+1:]:
                if (self.nodes[key_1], self.nodes[key_2]) in edge_set:
                    queue.put((self.nodes[key_1], self.nodes[key_2]))
                    queue.put((self.nodes[key_2], self.nodes[key_1]))

                    edge_set.remove((self.nodes[key_1], self.nodes[key_2]))
                    edge_set.remove((self.nodes[key_2], self.nodes[key_1]))

        return queue

    def ac3(self, queue: Queue):
        while not queue.empty():
            print(list(queue.queue))
            X_i, X_j = queue.get()
            print("Popped edge {}->{}".format(X_i, X_j))
            if self.revise(X_i, X_j):
                if len(X_i.domain) == 0:
                    print("No valid assignments. AC3 failed")
                    return False

                added_edges = []
                for X_k in sorted(self.edges[X_i].difference({X_j})):
                    queue.put((X_k, X_i))
                    added_edges.append((X_k, X_i))

                if len(added_edges) != 0:
                    print("Added edges: {}".format(added_edges))
                    print(self)

        print()
        print("Final graph's domain:")
        print(self)

    @staticmethod
    def satisfy(x, y):
        return x != y

    def revise(self, X_i: Node, X_j: Node):
        revised = False
        removed_vals = []
        for x in X_i.domain.copy():
            has_y_satisfying = False
            for y in X_j.domain:
                if Graph.satisfy(x, y):
                    has_y_satisfying = True
                    break

            if not has_y_satisfying:
                revised = True
                # delete x from D_i
                X_i.domain.remove(x)
                removed_vals.append(x)

        if revised:
            print("Edge {0}->{1}: removed {2} from {0}'s domain. New domain {3}".format(
                X_i, X_j, removed_vals, X_i.domain
            ))

        return revised

    def __str__(self):
        text = ""
        for node_key in sorted(self.nodes.keys()):
            text += "{}: {}\n".format(node_key, self.nodes[node_key].domain)
        return text
