import math
import numpy as np
import matplotlib.pyplot as plt
import gensim
import os
import collections
import smart_open
import random
import pickle
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import cosine


#veclist is the list of vector representations of semantics of financial assets
A = np.array(veclist)
semantic_linkage = 1-pairwise_distances(A, metric="cosine")

def has_cycle(edgelist,nodelist):
    try:
        if(type(edgelist[0])==list):
            edge_list = [compo[0] for compo in edgelist]
        else:
            edge_list = list(edgelist)
    except IndexError:
        edge_list = list(edgelist)
    node_list = list(nodelist)
    
    if (len(edge_list)<3):
        return False
    else:
        flatedge = sum(list(list(x) for x in edge_list),[])
        degree = [[x,flatedge.count(x)] for x in set(flatedge)] 
        if (1 not in sum(degree,[])[1::2]):
            return True
        for xnode in degree:
            if (xnode[1]<=1):
                node_list.remove(xnode[0])
                try:
                    edge_list.pop(sum(list(list(x) for x in edge_list),[]).index(xnode[0])/2)
                except ValueError:
                    continue
        return (has_cycle(edge_list,node_list))
    
def adjc(edgetuple, edgeslist, k):
    can1con = []
    can2con = []
    edge_list = list(edgeslist)
    m = list(edgetuple)
    for edge in edge_list:        
        if (type(edge)==tuple):
            if (m[0] in list(edge)):
                tail = list(edge)
                tail.remove(m[0])
                can1con = can1con+tail
            if (m[1] in list(edge)):
                tail = list(edge)
                tail.remove(m[1])
                can2con = can2con+tail        
        if (type(edge)==list):
            if (m[0] in list(edge[0])):
                tail = list(edge[0])
                tail.remove(m[0])
                tail = tail+list(edge[1])
                can1con = can1con+sorted(tail)
            if (m[1] in list(edge[0])):
                tail = list(edge[0])
                tail.remove(m[1])
                tail = tail+list(edge[1])
                can2con = can2con+sorted(tail)
    common = list(set([stdcomp for stdcomp in can1con if stdcomp in can2con]))
    if (len(common)>(k-1)):
        return (True, common)
    else:
        return (False, [])
        
def grow_semantic_vine(semantic_mtx):
    n_asset = len(semantic_mtx)
    #slist convert the semantic matrix to a ndarray：(('aapl', 'abt', s=?))
    slist = []
    for i in range(n_asset):
        for j in range(i):
            slist.append((i, j, semantic_mtx[i][j]))
    desclist = sorted(slist, key = lambda tuple: tuple[2], reverse=True)
    for k in range(n_asset-1):
        flag = 0
        if (k==0):
            nodes = [[]]
            edges = [[]]
            while (len(edges[k])<(n_asset-1)):
                if (not flag<len(desclist)):
                    flag = flag%len(desclist)
                del_pairwise = True
                #the first layer tree has no edge as nodes
                edges[k].append(desclist[flag][0:2])
                if (desclist[flag][0] not in nodes[k]):
                    nodes[k].append(desclist[flag][0])
                if (desclist[flag][1] not in nodes[k]):
                    nodes[k].append(desclist[flag][1])
                if (has_cycle(edges[k],nodes[k])):
                    del edges[k][-1]
                    del_pairwise = False 
                if (del_pairwise):
                    desclist.pop(flag) 
                flag=flag+1
        else:
            nodes.append([])
            edges.append([])
            while (len(edges[k])<(n_asset-1-k)):
                if (not flag<len(desclist)):
                    flag = flag%len(desclist)
                del_pairwise = True
                (is_adjc, conditionlist) = adjc(desclist[flag][0:2],edges[k-1],k)
                if (is_adjc):
                    edges[k].append([desclist[flag][0:2], conditionlist])
                    if (desclist[flag][0] not in nodes[k]):
                        nodes[k].append(desclist[flag][0])
                    if (desclist[flag][1] not in nodes[k]):
                        nodes[k].append(desclist[flag][1])
                    if (has_cycle(edges[k],nodes[k])):
                        del edges[k][-1]
                        del_pairwise = False 
                    if (del_pairwise):
                        desclist.pop(flag)
                flag=flag+1
            print('Tree'+str(k+1)+'built!')
    return (edges)

%time s_vine=grow_semantic_vine(semantic_linkage)
print ('the semantic vine: ', s_vine)