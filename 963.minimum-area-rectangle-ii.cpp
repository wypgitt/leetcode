// Translated from 963.minimum-area-rectangle-ii.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=963 lang=python3
// #
// # [963] Minimum Area Rectangle II
// #
// 
// # --- Interview notes (geometry, hashing diagonals, cross product area, complexity) ---
// #
// # Problem
// # Given **`points`** in the plane, choose **four distinct** points that are the vertices of a **rectangle** (edges not required
// # to be parallel to the axes). Return the **minimum** possible **area**, or **`0`** if no rectangle exists.
// #
// # Geometry — diagonals characterize a rectangle
// # In a **parallelogram**, diagonals **bisect** each other. In a **rectangle**, the two diagonals have **equal length**. So every
// # rectangle gives **two unordered pairs** of points (the two diagonals) that share:
// # • the **same midpoint** (**same bisector point**), and
// # • the **same squared Euclidean length** (**`dist²`** along either diagonal).
// #
// # Conversely, if two **disjoint** segments **PQ** and **RS** share a midpoint and have equal length, their four endpoints form a
// # **parallelogram with equal diagonals**, hence a **rectangle**. So valid rectangles correspond exactly to choosing **two distinct**
// # diagonal-pairs in the same **(midpoint, length²)** class whose four indices are all different.
// #
// # Why group by **(sx, sy, d²)** with **sx = x₁+x₂**, **sy = y₁+y₂**
// # The midpoint is **`((x₁+x₂)/2, (y₁+y₂)/2)`**. Using **integer** **`(x₁+x₂, y₁+y₂)`** avoids floating keys and uniquely fixes the
// # midpoint for integer coordinates. **`d² = (x₁-x₂)²+(y₁-y₂)²`** is the squared diagonal length (same for both diagonals of one
// # rectangle).
// #
// # Area without unstable midpoint arithmetic
// # Let **`D₁ = (xᵢ-xⱼ, yᵢ-yⱼ)`** and **`D₂ = (xₖ-xₗ, yₖ-yₗ)`** be vectors along the two diagonals (same length). If **`O`** is the
// # common midpoint and **`u = Pᵢ-O`**, **`v = Pₖ-O`** are half-diagonals to endpoints **`i`** and **`k`**, then
// # **`area = 2 · |u × v|`** (parallelogram spanned by **`u,v`** from **`O`** covers half the rectangle… standard derivation). Expanding
// # in coordinates yields the **integer-friendly** form:
// #
// # **`area = | (xᵢ-xⱼ)(yₖ-yₗ) - (yᵢ-yⱼ)(xₖ-xₗ) | / 2`**
// #
// # which equals **`| D₁ × D₂ | / 2`** (scalar **2D cross magnitude**). Endpoint order along each diagonal only flips signs → absolute
// # value unchanged.
// #
// # Algorithm
// # 1. Enumerate all unordered pairs **`(i, j)`**, **`i < j`**, append **`(i, j)`** to **`groups[(sx, sy, d²)]`**.
// # 2. For each bucket with **≥ 2** pairs, try every unordered pair of entries **`((i,j), (k,l))`**.
// # 3. If **`|{i,j,k,l}| = 4`**, compute **`area`** via the formula above; track minimum.
// # 4. Return **`0`** if **`n < 4`** or no valid rectangle found.
// #
// # Data structures
// # • **`defaultdict(list)`** — maps a diagonal signature to all pairs that share it (**`O(n²)`** entries total).
// # • No spatial tree needed — algebraic grouping is exact for this characterization.
// #
// # Time complexity
// # **`O(n²)`** pairs enumerated; processing buckets costs **`Σ_k C(m_k, 2)`** where **`m_k`** is bucket sizes. In worst-case patterns
// # many pairs could land in one bucket (**`O(n⁴)`** upper bound), but for typical **`n ≤ 500`** this passes; average random sets spread
// # pairs across buckets.
// #
// # Space complexity **`O(n²)`** for storing all unordered pairs (signature lists).
// #
// # Edge cases
// # • **Fewer than 4 points** — **`0`**.
// # • **Degenerate “rectangle”** (e.g. collinear)** — cross product **`0`**, area **`0`**; minimum might stay **`0`** if only degenerate
// #   configs exist (still consistent with “minimum area”).
// # • **Floating output** — LeetCode expects **`float`**; dividing by **`2.0`** is fine.
// #
// # Tests (sanity)
// # • Square corners **`(0,0),(0,1),(1,0),(1,1)`** → area **`1`**.
// # • **`2×1`** axis-aligned rectangle **`(0,0),(2,0),(2,1),(0,1)`** → area **`2`** (diagonals **`(0,0)-(2,1)`** and **`(0,1)-(2,0)`**).
// #
// # Improvements
// # • **Early pruning** — skip buckets with **`< 2`** pairs.
// # • **Numerical** — integer cross product until final **`/ 2.0`** minimizes FP error.
// #
// # --- end notes ---
// 
// # @lc code=start
// from collections import defaultdict
// from typing import List
// 
// 
// class Solution:
//     def minAreaFreeRect(self, points: List[List[int]]) -> float:
//         n = len(points)
//         if n < 4:
//             return 0.0
// 
//         groups = defaultdict(list)
//         for i in range(n):
//             xi, yi = points[i]
//             for j in range(i + 1, n):
//                 xj, yj = points[j]
//                 sx = xi + xj
//                 sy = yi + yj
//                 d2 = (xi - xj) ** 2 + (yi - yj) ** 2
//                 groups[(sx, sy, d2)].append((i, j))
// 
//         best = float("inf")
//         for lst in groups.values():
//             m = len(lst)
//             for a in range(m):
//                 i, j = lst[a]
//                 xi, yi = points[i]
//                 xj, yj = points[j]
//                 for b in range(a + 1, m):
//                     k, l = lst[b]
//                     if len({i, j, k, l}) < 4:
//                         continue
//                     xk, yk = points[k]
//                     xl, yl = points[l]
//                     cross = (xi - xj) * (yk - yl) - (yi - yj) * (xk - xl)
//                     area = abs(cross) / 2.0
//                     if area < best:
//                         best = area
// 
//         return 0.0 if best == float("inf") else best
// 
// 
// # @lc code=end

#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <deque>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

// C++ translation notes:
// - Python list/deque/heap/dict/set are translated to vector/deque/priority_queue/map or unordered_map/set.
// - TreeNode and ListNode are supplied by LeetCode. Define LOCAL_LEETCODE_STUBS for local-only compilation of tree/list solutions.
#ifdef LOCAL_LEETCODE_STUBS
struct ListNode {
    int val;
    ListNode* next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode* next) : val(x), next(next) {}
};
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode* left, TreeNode* right) : val(x), left(left), right(right) {}
};
#endif

class Solution {
public:
    double minAreaFreeRect(vector<vector<int>>& points) {
        int n = points.size();
        if (n < 4) return 0.0;
        map<tuple<int, int, int>, vector<pair<int, int>>> groups;
        for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) {
            int sx = points[i][0] + points[j][0];
            int sy = points[i][1] + points[j][1];
            int d2 = (points[i][0] - points[j][0]) * (points[i][0] - points[j][0]) + (points[i][1] - points[j][1]) * (points[i][1] - points[j][1]);
            groups[{sx, sy, d2}].push_back({i, j});
        }
        double best = numeric_limits<double>::infinity();
        for (auto& [_, lst] : groups) {
            for (int a = 0; a < (int)lst.size(); ++a) {
                auto [i, j] = lst[a];
                for (int b = a + 1; b < (int)lst.size(); ++b) {
                    auto [k, l] = lst[b];
                    set<int> ids{i, j, k, l};
                    if (ids.size() < 4) continue;
                    long long cross = 1LL * (points[i][0] - points[j][0]) * (points[k][1] - points[l][1]) - 1LL * (points[i][1] - points[j][1]) * (points[k][0] - points[l][0]);
                    best = min(best, abs(cross) / 2.0);
                }
            }
        }
        return isinf(best) ? 0.0 : best;
    }
};
