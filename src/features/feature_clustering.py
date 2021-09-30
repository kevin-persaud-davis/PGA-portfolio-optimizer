"""
Outline of Feature Clustering Process:

1. Project observed features into a metric space, resulting in
an observation matrix

    Metric space options:
        - Correlation based approach
            > section 4.4.1
        - information-theoretic concepts (variation of information)
            > section 3

2. Apply procedure to determine the optimal number and
composition of clusters

    Procedure options:
        - ONC algorithm
            > if silhouette scores are low, features may
            be a combination of multiple features across
            clusters and to combat this apply regressors 
            linear combinations of features within each cluster
    

"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples


# Base Clustering (Snippet 4.1)

def cluster_Kmeans_base(corr_0, max_num_clusters=10, n_init=10):
    x, silh = ((1-corr_0.fillna(0)) / 2.)**.5, pd.Series()
    
    for init in range(n_init):
        for i in iter(range(2, max_num_clusters)):
            kmeans_ = KMeans(n_clusters=i, n_init=1)
            kmeans_ = kmeans_.fit(x)
            silh_ = silhouette_samples(x, kmeans_.labels_)
            stat = (silh_.mean()/silh_.std(), silh.mean()/silh.std())

            if np.isnan(stat[1]) or stat[0] > stat[1]:
                silh, kmeans = silh_, kmeans_

    new_idx = np.argsort(kmeans.labels_)
    corr_1 = corr_0.iloc[new_idx]

    corr_1 = corr_1.iloc[:, new_idx]
    clstrs = {i:corr_0.columns[np.where(kmeans.labels_==i)[0]].tolist()
            for i in np.unique(kmeans.labels_)} 
    silh = pd.Series(silh, index=x.index)
    return corr_1, clstrs, silh

# Top-level of Clustering (snippet 4.2)

def make_new_outputs(corr_0, clstrs, clstrs_2):

    clstrs_new = {}
    for i in clstrs.keys():
        clstrs_new[len(clstrs_new.keys())] = list(clstrs[i])

    for i in clstrs_2.keys():
        clstrs_new[len(clstrs_new.keys())] = list(clstrs_2[i])

    new_idx = [j for i in clstrs_new for j in clstrs_new[i]]
    corr_new = corr_0.lco[new_idx, new_idx]

    x = ((1 - corr_0.fillna(0))/2.)**.5
    kmeans_labels = np.zeros(len(x.columns))
    for i in clstrs_new.keys():
        idxs = [x.index.get_loc(k) for k in clstrs_new[i]]
        kmeans_labels[idxs] = i

    silh_new = pd.Series(silhouette_samples(x, kmeans_labels), index=x.index)
    
    return corr_new, clstrs_new, silh_new

def cluster_Kmeans_top(corr_0, max_num_clusters=None, n_init=10):
    
    if max_num_clusters == None:
        max_num_clusters = corr_0.shape[1] - 1 
    
    corr_1, clstrs, silh = cluster_Kmeans_base(corr_0, 
                        max_num_clusters=min(max_num_clusters, corr_0.shape[1] - 1), 
                        n_init=n_init)
    cluster_tstats = {i : np.mean(silh[clstrs[i]]) / np.std(silh[clstrs[i]])
                    for i in clstrs.keys()}
    
    tstat_mean = sum(cluster_tstats.values()) / len(cluster_tstats)
    redo_clusters = [i for i in cluster_tstats.keys() 
                    if cluster_tstats[i] < tstat_mean]
    
    if len(redo_clusters) <= 1:
        return corr_1, clstrs, silh
    else:
        keys_redo = [j for i in redo_clusters for j in clstrs[i]]
        corr_temp = corr_0.loc[keys_redo, keys_redo]

        tstat_mean = np.mean([cluster_tstats[i] for i in redo_clusters])
        corr_2, clstrs_2, silh_2 = cluster_Kmeans_top(corr_temp,
                                max_num_clusters=min(max_num_clusters, corr_temp.shape[-1]-1),
                                n_init=n_init)
    
        corr_new, clstrs_new, silh_new = make_new_outputs(corr_0,
                                                    {i:clstrs[i] 
                                                    for i in clstrs.keys() if i not in redo_clusters},
                                                    clstrs_2)
        new_tstat_mean = np.mean([np.mean(silh_new[clstrs_new[i]])/
                                np.std(silh_new[clstrs_new[i]]) for i in clstrs_new.keys()])
        
        if new_tstat_mean <= tstat_mean:
            return corr_1, clstrs, silh
        else:
            return corr_new, clstrs_new, silh_new
        

if __name__ == "__main__":
    pass