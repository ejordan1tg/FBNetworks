import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import glob
from scipy.stats import skew

# Collect metrics
densities = []
all_degrees = []
clustering_coeffs = []
avg_clustering_coeffs = []
largest_cc_sizes = []
num_nodes = []
num_edges = []

for file in glob.glob('C:/Users/Elijah/FBNetworks/AdjMatrices_1/*.npy'):
    mat = np.load(file)
    if mat.size == 0 or min(mat.shape) ==0:
        continue
    G = nx.from_numpy_array(mat)
    
    # Density
    dens = nx.density(G)
    densities.append(dens)
    
    # Degree distribution
    degrees = [d for n, d in G.degree()]
    all_degrees.extend(degrees)
    
    # Clustering coefficients
    node_clust = list(nx.clustering(G).values())
    clustering_coeffs.extend(node_clust)
    avg_clustering_coeffs.append(np.mean(node_clust))
    
    # Largest connected component size
    if G.number_of_nodes() > 0:
        lcc = max((len(c) for c in nx.connected_components(G)), default=0)
    else:
        lcc = 0
    largest_cc_sizes.append(lcc)
    
    # Size distribution
    num_nodes.append(G.number_of_nodes())
    num_edges.append(G.number_of_edges())

# Compute statistics

def describe(arr):
    return {
        'mean': np.mean(arr),
        'median': np.median(arr),
        'stdev': np.std(arr),
        'variance': np.var(arr),
        'skewness': skew(arr)
    }

density_stats = describe(densities)
degree_stats = describe(all_degrees)
clustering_stats = describe(clustering_coeffs)
lcc_stats = describe(largest_cc_sizes)
size_stats = {
    'nodes': describe(num_nodes),
    'edges': describe(num_edges)
}

print(density_stats)

# Plot histograms
metrics = {
    'Density': densities,
    'Degree': all_degrees,
    'Clustering Coefficient': clustering_coeffs,
    'Average Clustering Coefficient': avg_clustering_coeffs,
    'Largest Connected Component Size': largest_cc_sizes,
    'Number of Nodes': num_nodes,
    'Number of Edges': num_edges
}

for name, data in metrics.items():
    plt.figure()
    plt.hist(data, bins=30)
    plt.title(f'Histogram of {name}')
    plt.xlabel(name)
    plt.ylabel('Frequency')
    plt.savefig(f'{name.replace(" ", "_").lower()}_histogram.png')
    plt.close()



