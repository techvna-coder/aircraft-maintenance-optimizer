import numpy as np
from sklearn.cluster import KMeans

def choose_k_elbow(X, k_min=2, k_max=8):
    """Chọn k theo elbow (inertia) – nhanh và ổn định."""
    inertias, models = [], []
    k_max = max(k_min, k_max)
    for k in range(k_min, k_max+1):
        if k > len(X):
            break
        km = KMeans(n_clusters=k, random_state=42, n_init=5, algorithm="elkan").fit(X)
        inertias.append(km.inertia_)
        models.append(km)
    if not models:
        # fallback
        return KMeans(n_clusters=2, random_state=42, n_init=5, algorithm="elkan").fit(X), 2

    if len(inertias) == 1:
        return models[0], models[0].n_clusters

    drops = np.diff(inertias)
    first_drop = abs(drops[0]) if drops[0] != 0 else 1e-9
    rel = np.abs(drops) / first_drop
    idx = next((i for i, r in enumerate(rel) if r < 0.1), len(models)-1)  # giảm <10% so với drop đầu
    return models[idx], models[idx].n_clusters

def kmeans_cluster_1d(X, model):
    labels = model.predict(X)
    centers = model.cluster_centers_.flatten()
    return labels, centers
