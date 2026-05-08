/*
 * @lc app=leetcode id=2613 lang=cpp
 *
 * [2613] Beautiful Pairs
 */
// Translated from 2613.beautiful-pairs.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=2613 lang=python3
// #
// # [2613] Beautiful Pairs
// #
// # --- Notes (problem, geometry, duplicates, divide & conquer, strip, lex tie-break, complexity, interview) ---
// #
// # Problem restatement
// # Two arrays nums1, nums2 of equal length n define points P_i = (nums1[i], nums2[i]) in the plane.
// # Among all index pairs (i, j) with i < j, minimize the Manhattan distance
// #   |nums1[i] - nums1[j]| + |nums2[i] - nums2[j]|.
// # Return such a pair; if several pairs achieve the minimum distance, return the lexicographically
// # smallest (compare i first, then j).
// #
// # Duplicate coordinates (distance 0)
// # If two distinct indices share the same point, the minimum distance is 0. Among all pairs at
// # distance 0, the lexicographically smallest pair is always (a, b) where a and b are the two
// # smallest indices that share some duplicated coordinate — globally, take the minimum over each
// # duplicate group’s first two indices in sorted order, then pick the minimum pair in lex order.
// # Implementation: group indices by (nums1[i], nums2[i]); for any group with >= 2 indices (stored in
// # increasing index order), candidate pair (idx[0], idx[1]); answer is min of those candidates.
// #
// # Otherwise — closest pair under L1 (Manhattan) metric
// # Classical computational geometry: closest pair of points in the plane under Manhattan distance.
// # Euclidean closest pair uses divide & conquer O(n log n); Manhattan / L1 admits the same outline:
// #   - Sort points by x-coordinate (tie-break y, then index for determinism).
// #   - Split by median x in [l, r]; recursively solve left and right halves; let best distance be d.
// #   - Merge: cross pairs may have one point in each half. Keep points whose x lies within d of the
// #     vertical strip around the median x; sort strip by y; for each point, compare only to the next
// #     few points in y-order — when y-gap exceeds current best d, inner loop breaks (same pruning as
// #     Euclidean closest pair).
// # Tie-breaking on equal distance: when comparing candidate pairs, prefer smaller (i, j) lex order
// # with i < j (indices from original arrays).
// #
// # Why this algorithm
// # Brute force O(n^2) is too slow for n ≈ 10^5. Plane sweep / segment-tree variants exist for L1, but
// # divide & conquer + strip is standard, fits interviews, and hits O(n log n) under usual analysis.
// #
// # Data structures
// # - List of tuples (x, y, index) for points.
// # - defaultdict(list) for duplicate grouping.
// # - Temporary strip lists sorted by y — O(k log k) per merge level; overall O(n log n).
// #
// # Time complexity
// # - Duplicates: O(n) grouping.
// # - Divide & conquer closest pair: O(n log n) typical for Manhattan with strip pruning.
// #
// # Space complexity
// # - O(n) for points, recursion stack O(log n), strip arrays O(n) per level worst case — O(n) total.
// #
// # Edge cases
// # - n == 2: single pair.
// # - Many coincident points: duplicate branch.
// # - Collinear vertical strip: strip pruning still safe with break on y difference > d.
// #
// # Improvements / alternatives
// # - Sorting + segment trees over nums1 (walkccc-style) for different trade-offs when coordinate ranges
// #   are bounded and suitable for indexing.
// # - Randomized incremental would be unusual here; DC remains the textbook answer.
// #
// # LeetCode submission
// # Import inside # lc-original code=start so List / defaultdict are defined on submit.
// #
// # Interview walkthrough
// # 1) Map indices to points; note Manhattan = L1 metric.
// # 2) Handle distance 0 duplicates first with lex-smallest pair among duplicate groups.
// # 3) Closest pair: sort by x, recurse, merge with vertical strip + sort by y + neighbor checks.
// # 4) Tie-break on equal distance with lex order on (i, j).
// # --- end notes ---
// 
// # lc-original code=start
// from collections import defaultdict
// from typing import List, Optional, Tuple
// 
// _INF = 10**18
// 
// 
// class Solution:
//     def beautifulPair(self, nums1: List[int], nums2: List[int]) -> List[int]:
//         n = len(nums1)
// 
//         def manhattan(x1: int, y1: int, x2: int, y2: int) -> int:
//             return abs(x1 - x2) + abs(y1 - y2)
// 
//         def better(d1: int, i1: int, j1: int, d2: int, i2: int, j2: int) -> bool:
//             """True iff candidate (d2, i2, j2) beats (d1, i1, j1)."""
//             if d2 < d1:
//                 return True
//             if d2 > d1:
//                 return False
//             return (i2, j2) < (i1, j1)
// 
//         groups = defaultdict(list)
//         for i in range(n):
//             groups[(nums1[i], nums2[i])].append(i)
// 
//         best_dup: Optional[Tuple[int, int]] = None
//         for idxs in groups.values():
//             if len(idxs) >= 2:
//                 cand = (idxs[0], idxs[1])
//                 if best_dup is None or cand < best_dup:
//                     best_dup = cand
//         if best_dup is not None:
//             return [best_dup[0], best_dup[1]]
// 
//         pts = [(nums1[i], nums2[i], i) for i in range(n)]
//         pts.sort(key=lambda t: (t[0], t[1], t[2]))
// 
//         def dfs(l: int, r: int) -> tuple[int, int, int]:
//             if l >= r:
//                 return (_INF, -1, -1)
//             m = (l + r) >> 1
//             x_mid = pts[m][0]
//             d1, a1, b1 = dfs(l, m)
//             d2, a2, b2 = dfs(m + 1, r)
//             if better(d1, a1, b1, d2, a2, b2):
//                 d1, a1, b1 = d2, a2, b2
//             strip = [p for p in pts[l : r + 1] if abs(p[0] - x_mid) <= d1]
//             strip.sort(key=lambda p: p[1])
//             sz = len(strip)
//             for i in range(sz):
//                 for j in range(i + 1, sz):
//                     if strip[j][1] - strip[i][1] > d1:
//                         break
//                     ii, jj = sorted((strip[i][2], strip[j][2]))
//                     d = manhattan(strip[i][0], strip[i][1], strip[j][0], strip[j][1])
//                     if better(d1, a1, b1, d, ii, jj):
//                         d1, a1, b1 = d, ii, jj
//             return (d1, a1, b1)
// 
//         _, pi, pj = dfs(0, len(pts) - 1)
//         return [pi, pj]
// 
// 
// # lc-original code=end

// @lc code=start
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
    static constexpr long long INF = (long long)1e18;

    long long manhattan(long long x1, long long y1, long long x2, long long y2) {
        return llabs(x1 - x2) + llabs(y1 - y2);
    }

    bool better(long long d1, int i1, int j1, long long d2, int i2, int j2) {
        if (d2 != d1) return d2 < d1;
        return pair<int, int>{i2, j2} < pair<int, int>{i1, j1};
    }

public:
    vector<int> beautifulPair(vector<int>& nums1, vector<int>& nums2) {
        int n = nums1.size();
        map<pair<int, int>, vector<int>> groups;
        for (int i = 0; i < n; ++i) groups[{nums1[i], nums2[i]}].push_back(i);
        pair<int, int> bestDup{INT_MAX, INT_MAX};
        for (auto& [_, idxs] : groups) if (idxs.size() >= 2) bestDup = min(bestDup, {idxs[0], idxs[1]});
        if (bestDup.first != INT_MAX) return {bestDup.first, bestDup.second};
        vector<array<int, 3>> pts;
        for (int i = 0; i < n; ++i) pts.push_back({nums1[i], nums2[i], i});
        sort(pts.begin(), pts.end());
        function<tuple<long long, int, int>(int, int)> dfs = [&](int l, int r) -> tuple<long long, int, int> {
            if (l >= r) return {INF, -1, -1};
            int m = (l + r) / 2;
            int xmid = pts[m][0];
            auto [d1, a1, b1] = dfs(l, m);
            auto [d2, a2, b2] = dfs(m + 1, r);
            if (better(d1, a1, b1, d2, a2, b2)) tie(d1, a1, b1) = tuple<long long, int, int>{d2, a2, b2};
            vector<array<int, 3>> strip;
            for (int i = l; i <= r; ++i) if (llabs((long long)pts[i][0] - xmid) <= d1) strip.push_back(pts[i]);
            sort(strip.begin(), strip.end(), [](auto& a, auto& b) { return a[1] < b[1]; });
            for (int i = 0; i < (int)strip.size(); ++i) {
                for (int j = i + 1; j < (int)strip.size(); ++j) {
                    if (strip[j][1] - strip[i][1] > d1) break;
                    int ii = min(strip[i][2], strip[j][2]), jj = max(strip[i][2], strip[j][2]);
                    long long d = manhattan(strip[i][0], strip[i][1], strip[j][0], strip[j][1]);
                    if (better(d1, a1, b1, d, ii, jj)) tie(d1, a1, b1) = tuple<long long, int, int>{d, ii, jj};
                }
            }
            return {d1, a1, b1};
        };
        auto [_, i, j] = dfs(0, n - 1);
        return {i, j};
    }
};
// @lc code=end
