#include <algorithm>
#include <array>
#include <climits>
#include <cmath>
#include <condition_variable>
#include <cstdlib>
#include <deque>
#include <functional>
#include <map>
#include <mutex>
#include <numeric>
#include <queue>
#include <set>
#include <sstream>
#include <stack>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

class Solution {
public:
    int minimumCost(int n, vector<vector<int>>& connections) {
        sort(connections.begin(), connections.end(), [](const auto& a, const auto& b) {
            return a[2] < b[2];
        });

        DSU dsu(n + 1);
        int cost = 0;
        int used = 0;
        for (const auto& edge : connections) {
            if (dsu.unite(edge[0], edge[1])) {
                cost += edge[2];
                ++used;
            }
        }

        return used == n - 1 ? cost : -1;
    }

private:
    struct DSU {
        vector<int> parent;
        vector<int> rank;

        DSU(int n) : parent(n), rank(n, 0) {
            iota(parent.begin(), parent.end(), 0);
        }

        int find(int x) {
            if (parent[x] != x) parent[x] = find(parent[x]);
            return parent[x];
        }

        bool unite(int a, int b) {
            int rootA = find(a), rootB = find(b);
            if (rootA == rootB) return false;
            if (rank[rootA] < rank[rootB]) swap(rootA, rootB);
            parent[rootB] = rootA;
            if (rank[rootA] == rank[rootB]) ++rank[rootA];
            return true;
        }
    };
};

/*
Interview Explanation

Core idea:
Connecting all cities at minimum cost is a Minimum Spanning Tree problem.
Kruskal's algorithm adds the cheapest edge that connects two different
components.

C++ data structures:
- sort orders edges by cost.
- DSU/Union-Find tracks connected components with path compression and rank.

Algorithm:
1. Sort connections by weight.
2. For each edge, union its endpoints if they are in different components.
3. Add its cost when used.
4. If exactly n-1 edges are used, return cost; otherwise the graph is
   disconnected.

Correctness:
Kruskal's cut property says the cheapest edge crossing any component cut is
safe to add to an MST. DSU prevents cycles. Thus the algorithm builds a
minimum-cost spanning tree when one exists.

Complexity:
Sorting costs O(E log E). DSU operations are nearly O(1), so total time is
O(E log E). Space is O(n).

Edge cases:
- Disconnected graph returns -1.
- Already connected with n-1 edges works.
- City labels are 1-indexed, so DSU size is n+1.
*/
