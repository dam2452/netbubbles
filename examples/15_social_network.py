"""Example 15: Social network — follower/interaction graph."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import netbubbles as nb
from netbubbles.presets import social

OUT = "example_output"

# Simulated social network edges: (follower, followed, interactions)
edges = [
    ("Alice", "Bob", 12),
    ("Alice", "Carol", 8),
    ("Alice", "Dave", 3),
    ("Bob", "Alice", 10),
    ("Bob", "Eve", 7),
    ("Carol", "Alice", 5),
    ("Carol", "Dave", 9),
    ("Carol", "Frank", 4),
    ("Dave", "Carol", 6),
    ("Dave", "Grace", 11),
    ("Eve", "Bob", 8),
    ("Eve", "Frank", 5),
    ("Frank", "Carol", 3),
    ("Frank", "Grace", 7),
    ("Grace", "Dave", 9),
    ("Grace", "Heidi", 6),
    ("Heidi", "Grace", 4),
    ("Heidi", "Alice", 2),
    ("Heidi", "Ivan", 10),
    ("Ivan", "Heidi", 8),
    ("Ivan", "Judy", 5),
    ("Judy", "Ivan", 6),
    ("Judy", "Alice", 3),
]

# Detect communities via label propagation
g_temp = social.from_edge_list(edges)
clusters = social.detect_clusters(g_temp)

g = social.from_edge_list(edges, clusters=clusters)
ax = nb.draw(g, title="Social Network", subtitle="10 users, color by community")
ax.figure.savefig(f"{OUT}/15_social_network.png", dpi=150, bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/15_social_network.png")
