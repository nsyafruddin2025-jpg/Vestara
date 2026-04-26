"""
Peer Clustering — KMeans (k=4) unsupervised ML layer for Vestara.

Clusters users into financial archetypes based on the same 7-feature space
as the GradientBoostingRegressor, enabling peer benchmarking without labels.

MGMT 655 Week 5: Unsupervised ML requirement.

Design notes:
- Archetype labels derived programmatically from post-hoc sort on
  mean disposable_income — no hardcoded cluster-to-label mapping.
- StandardScaler applied before KMeans (distance-based, scaling mandatory).
- Singleton get_clusterer(n_samples) trains once per session.
- Thread safety: not guaranteed under Streamlit multi-threading;
  acceptable for single-user deployment (known limitation, COC §4).
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from dataclasses import dataclass

from vestara.data.synthetic_data import generate_regression_dataset, REGRESSION_FEATURES


# ── Archetype definitions — ordered by ascending financial capacity ──────────
# These are the 4 archetypes assigned in order of ascending mean disposable_income.
# Order: lowest → highest capacity. Do NOT reorder.

_ARCHETYPES_ORDERED = [
    {
        "label": "Early Saver",
        "icon": "🌱",
        "color": "#F59E0B",
        "description": (
            "You are in the early stage of your financial journey. "
            "Your peers in this group typically have lower disposable income "
            "but strong goal commitment. Focus on building income and "
            "keeping expenses tight."
        ),
    },
    {
        "label": "Steady Climber",
        "icon": "📈",
        "color": "#06B6D4",
        "description": (
            "You have stable income and moderate savings capacity. "
            "Your peer group consistently achieves mid-range goals within "
            "7–12 years. Consistent monthly investment is your biggest lever."
        ),
    },
    {
        "label": "Aggressive Accumulator",
        "icon": "🚀",
        "color": "#7C3AED",
        "description": (
            "You have above-average disposable income relative to your goal size. "
            "Your peer group tends to over-achieve goals ahead of schedule. "
            "Consider shortening your timeline or upgrading your goal."
        ),
    },
    {
        "label": "High Earner",
        "icon": "💎",
        "color": "#10B981",
        "description": (
            "You are in the top income tier among Vestara users. "
            "Your peer group can sustain high monthly contributions across "
            "multiple goals simultaneously. Diversification is key."
        ),
    },
]


@dataclass
class ClusterResult:
    archetype: str
    cluster_id: int
    description: str
    color: str
    icon: str
    peer_count: int
    peer_median_salary: float
    peer_median_disposable: float
    peer_median_goal_cost: float
    peer_median_timeline: float
    user_vs_peers: dict


class PeerClusterer:
    FEATURES = REGRESSION_FEATURES
    N_CLUSTERS = 4

    def __init__(self):
        self._kmeans: KMeans | None = None
        self._scaler: StandardScaler | None = None
        self._cluster_to_archetype: dict[int, dict] = {}
        self._peer_data: pd.DataFrame | None = None
        self._is_trained = False

    @property
    def is_trained(self) -> bool:
        return self._is_trained

    def train(self, n_samples: int = 2000) -> dict:
        df = generate_regression_dataset(n_samples)
        self._peer_data = df[self.FEATURES].copy()

        X = self._peer_data.values

        self._scaler = StandardScaler()
        X_scaled = self._scaler.fit_transform(X)

        self._kmeans = KMeans(
            n_clusters=self.N_CLUSTERS,
            init="k-means++",
            n_init="auto",
            random_state=42,
        )
        self._kmeans.fit(X_scaled)

        labels = self._kmeans.labels_
        self._peer_data = self._peer_data.copy()
        self._peer_data["cluster"] = labels

        # Derive archetype mapping programmatically — sort clusters by
        # ascending mean disposable_income, then assign _ARCHETYPES_ORDERED in order.
        cluster_mean_disposable = (
            self._peer_data.groupby("cluster")["disposable_income"]
            .mean()
            .sort_values()
        )
        self._cluster_to_archetype = {
            int(cluster_id): _ARCHETYPES_ORDERED[rank]
            for rank, cluster_id in enumerate(cluster_mean_disposable.index)
        }

        self._is_trained = True

        return {
            "inertia": float(self._kmeans.inertia_),
            "cluster_sizes": {
                self._cluster_to_archetype[k]["label"]: int(v)
                for k, v in pd.Series(labels).value_counts().items()
            },
        }

    def predict(
        self,
        monthly_salary: float,
        city_living_cost_index: int,
        goal_cost: float,
        timeline_years: int,
        income_growth_rate: float,
        monthly_living_cost: float,
        disposable_income: float,
    ) -> ClusterResult:
        if not self._is_trained:
            raise RuntimeError("PeerClusterer not trained. Call .train() first.")

        user_vec = np.array([[
            monthly_salary,
            city_living_cost_index,
            goal_cost,
            timeline_years,
            income_growth_rate,
            monthly_living_cost,
            disposable_income,
        ]])

        user_scaled = self._scaler.transform(user_vec)
        cluster_id = int(self._kmeans.predict(user_scaled)[0])
        archetype_def = self._cluster_to_archetype[cluster_id]

        peers = self._peer_data[self._peer_data["cluster"] == cluster_id]
        peer_count = len(peers)
        peer_median_salary = float(peers["monthly_salary"].median())
        peer_median_disposable = float(peers["disposable_income"].median())
        peer_median_goal_cost = float(peers["goal_cost"].median())
        peer_median_timeline = float(peers["timeline_years"].median())

        def pct_diff(user_val: float, peer_val: float) -> float:
            if peer_val == 0:
                return 0.0
            return round((user_val - peer_val) / peer_val * 100, 1)

        user_vs_peers = {
            "salary_vs_peers_pct": pct_diff(monthly_salary, peer_median_salary),
            "disposable_vs_peers_pct": pct_diff(disposable_income, peer_median_disposable),
            "goal_vs_peers_pct": pct_diff(goal_cost, peer_median_goal_cost),
            "timeline_vs_peers_pct": pct_diff(timeline_years, peer_median_timeline),
        }

        return ClusterResult(
            archetype=archetype_def["label"],
            cluster_id=cluster_id,
            description=archetype_def["description"],
            color=archetype_def["color"],
            icon=archetype_def["icon"],
            peer_count=peer_count,
            peer_median_salary=peer_median_salary,
            peer_median_disposable=peer_median_disposable,
            peer_median_goal_cost=peer_median_goal_cost,
            peer_median_timeline=peer_median_timeline,
            user_vs_peers=user_vs_peers,
        )


# ── Module-level singleton ───────────────────────────────────────────────────

_clusterer: PeerClusterer | None = None


def get_clusterer(n_samples: int = 2000) -> PeerClusterer:
    """
    Returns a trained PeerClusterer singleton.
    Retrains if not yet initialized. n_samples controls synthetic peer pool size.
    Note: not thread-safe — acceptable for single-user deployment.
    """
    global _clusterer
    if _clusterer is None or not _clusterer.is_trained:
        _clusterer = PeerClusterer()
        _clusterer.train(n_samples=n_samples)
    return _clusterer
