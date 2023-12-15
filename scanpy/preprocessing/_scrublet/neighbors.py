from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import numpy as np

from ... import logging as logg

if TYPE_CHECKING:
    from numpy.typing import NDArray

    from ..._utils import AnyRandom

AnnoyDist = Literal["angular", "euclidean", "manhattan", "hamming", "dot"]


def get_knn_graph(
    X,
    k: int = 5,
    *,
    dist_metric: AnnoyDist = "euclidean",
    approx: bool = False,
    random_seed: AnyRandom = 0,
) -> NDArray[np.intp]:
    """
    Build k-nearest-neighbor graph
    Return edge list and nearest neighbor matrix
    """
    from sklearn.neighbors import NearestNeighbors

    if approx:
        try:
            from annoy import AnnoyIndex
        except ImportError as e:
            raise ValueError(
                'Could not find library "annoy" for approx. nearest neighbor search'
            ) from e
        t0 = logg.info("Using approximate nearest neighbor search")

        if dist_metric == "cosine":
            dist_metric = "angular"
        npc = X.shape[1]
        ncell = X.shape[0]
        annoy_index = AnnoyIndex(npc, metric=dist_metric)
        annoy_index.set_seed(random_seed)

        for i in range(ncell):
            annoy_index.add_item(i, list(X[i, :]))
        annoy_index.build(10)  # 10 trees

        knn = np.array(
            [annoy_index.get_nns_by_item(c, k + 1)[1:] for c in range(ncell)],
            dtype=np.intp,
        )
    else:
        t0 = logg.info("Using sklearn NearestNeighbors")

        if dist_metric == "cosine":
            nbrs = NearestNeighbors(
                n_neighbors=k, metric=dist_metric, algorithm="brute"
            ).fit(X)
        else:
            nbrs = NearestNeighbors(n_neighbors=k, metric=dist_metric).fit(X)
        knn: NDArray[np.intp] = nbrs.kneighbors(return_distance=False)

    logg.info("kNN graph built in {time_passed:.3} sec", time=t0)

    return knn
