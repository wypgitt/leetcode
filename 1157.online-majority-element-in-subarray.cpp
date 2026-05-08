// Translated from 1157.online-majority-element-in-subarray.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=1157 lang=python3
// #
// # [1157] Online Majority Element In Subarray
// #
// 
// # --- Interview notes (majority + segment tree merge, verification, complexity, constraints, alternatives) ---
// #
// # Problem
// # Preprocess array `arr`. Each query(left, right, threshold) asks: is there a value that appears **at least**
// # `threshold` times in arr[left..right] inclusive? Return such a value, or -1. Up to 1e4 queries on |arr| <= 2e4.
// #
// # Constraint (critical)
// # `2 * threshold > (right - left + 1)` i.e. threshold > half the subarray length. So any valid answer would have to be a
// # **strict majority** in the usual sense (more than half). At most one distinct value can satisfy the frequency check.
// #
// # Why not scan each query in O(range length)?
// # Worst-case O(queries * n) is too slow for n, queries ~ 1e4–2e4.
// #
// # Plan — two phases
// # (1) **Candidate** x that *could* be the majority on [L, R], in O(log n) time.
// # (2) **Verify** frequency of x on [L, R], in O(log n) time. If count >= threshold return x else -1.
// #
// # Phase 1 — Boyer–Moore majority merge on a segment tree
// # Boyer–Moore voting finds a majority element in one pass if one exists (> n/2 copies). For subarrays we cannot afford a
// # linear scan per query. Observation: the same “candidate + relative count” pairing can be **merged** like associative
// # folds over contiguous blocks (same idea as parallel BM).
// #
// # Merge two adjacent intervals with summaries (v1, c1) and (v2, c2):
// #   • If v1 == v2 → (v1, c1 + c2)
// #   • Else if c1 > c2 → (v1, c1 - c2)   # cancel opposing votes
// #   • Else → (v2, c2 - c1)
// # Leaves store (arr[i], 1). Internal nodes merge children. Range query merges O(log n) canonical segments → O(log n).
// #
// # If a strict majority exists on [L,R], its value is **always** the candidate produced by this merge (standard fact).
// # If no majority exists, the candidate is arbitrary garbage for our purpose — verification fails.
// #
// # Phase 2 — Frequency via sorted positions per value
// # Build `pos[value] = sorted list of indices where arr[index] == value`. Count of value x in [L,R] is:
// #   bisect_right(pos[x], R) - bisect_left(pos[x], L)   → O(log n) per query.
// #
// # Why this data structure for verification?
// # • Values up to 20000 — coarse bucket map is fine.
// # • Sorted indices + bisect beats scanning and pairs naturally with offline preprocessing O(n).
// #
// # Time complexity
// # • Build positions map: O(n). Build segment tree: O(n).
// # • Each query: O(log n) segment-tree walk + O(log n) bisects → **O(log n)**.
// #
// # Space complexity
// # • Positions store each index once: O(n). Segment tree ~4n nodes: **O(n)**.
// #
// # Edge cases
// # • threshold equals subarray length → verify candidate count == length.
// # • No majority / frequency below threshold → verification returns -1 even if candidate looks plausible after BM merge.
// #
// # Tests (statement)
// # arr = [1,1,2,2,1,1]
// # query(0,5,4) → value 1 appears 4 times → 1
// # query(0,3,3) → no value ≥ 3 times in [1,1,2,2] → -1
// # query(2,3,2) → [2,2] → 2
// #
// # Alternative approaches (trade-offs)
// # • **Random sampling** (problem hints): sample random indices in [L,R]; check arr[k]. Probability ≥ 1/2 each trial if a
// #   majority exists; repeat ~40–60 times for negligible failure — expected O(k log n) per query with verification. Randomized,
// #   not deterministic.
// # • **Wavelet tree / persistent structures**: heavier; overkill for interviews unless already familiar.
// # • **Square decomposition**: O(√n) or similar per query.
// #
// # Improvements
// # • Iterative segment tree to avoid recursion overhead (same asymptotics).
// # • Single bisect on `pos[candidate]` after query.
// #
// # --- end notes ---
// 
// # @lc code=start
// from bisect import bisect_left, bisect_right
// from collections import defaultdict
// from typing import List
// 
// 
// class MajorityChecker:
//     def __init__(self, arr: List[int]):
//         self.arr = arr
//         n = len(arr)
//         self.pos = defaultdict(list)
//         for i, x in enumerate(arr):
//             self.pos[x].append(i)
//         self.n = n
//         self.tree = [(0, 0)] * (4 * n)
//         self._build(1, 0, n - 1)
// 
//     def _merge(self, a, b):
//         v1, c1 = a
//         v2, c2 = b
//         if v1 == v2:
//             return (v1, c1 + c2)
//         if c1 > c2:
//             return (v1, c1 - c2)
//         return (v2, c2 - c1)
// 
//     def _build(self, node, l, r):
//         if l == r:
//             self.tree[node] = (self.arr[l], 1)
//             return
//         m = (l + r) // 2
//         self._build(node * 2, l, m)
//         self._build(node * 2 + 1, m + 1, r)
//         self.tree[node] = self._merge(self.tree[node * 2], self.tree[node * 2 + 1])
// 
//     def _query(self, node, l, r, ql, qr):
//         if ql <= l and r <= qr:
//             return self.tree[node]
//         if r < ql or l > qr:
//             return (0, 0)
//         m = (l + r) // 2
//         left = self._query(node * 2, l, m, ql, qr)
//         right = self._query(node * 2 + 1, m + 1, r, ql, qr)
//         return self._merge(left, right)
// 
//     def query(self, left: int, right: int, threshold: int) -> int:
//         cand, _ = self._query(1, 0, self.n - 1, left, right)
//         lst = self.pos.get(cand, [])
//         cnt = bisect_right(lst, right) - bisect_left(lst, left)
//         return cand if cnt >= threshold else -1
// 
// 
// # Your MajorityChecker object will be instantiated and called as such:
// # obj = MajorityChecker(arr)
// # param_1 = obj.query(left,right,threshold)
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

class MajorityChecker {
    vector<int> arr;
    unordered_map<int, vector<int>> pos;
    vector<pair<int, int>> tree;
    int n;

    pair<int, int> mergeNode(pair<int, int> a, pair<int, int> b) {
        auto [v1, c1] = a;
        auto [v2, c2] = b;
        if (v1 == v2) return {v1, c1 + c2};
        if (c1 > c2) return {v1, c1 - c2};
        return {v2, c2 - c1};
    }

    void build(int node, int l, int r) {
        if (l == r) {
            tree[node] = {arr[l], 1};
            return;
        }
        int m = (l + r) / 2;
        build(node * 2, l, m);
        build(node * 2 + 1, m + 1, r);
        tree[node] = mergeNode(tree[node * 2], tree[node * 2 + 1]);
    }

    pair<int, int> queryNode(int node, int l, int r, int ql, int qr) {
        if (ql <= l && r <= qr) return tree[node];
        if (r < ql || qr < l) return {0, 0};
        int m = (l + r) / 2;
        return mergeNode(queryNode(node * 2, l, m, ql, qr), queryNode(node * 2 + 1, m + 1, r, ql, qr));
    }

public:
    MajorityChecker(vector<int>& arr) : arr(arr), n(arr.size()), tree(4 * arr.size()) {
        for (int i = 0; i < n; ++i) pos[arr[i]].push_back(i);
        build(1, 0, n - 1);
    }

    int query(int left, int right, int threshold) {
        int cand = queryNode(1, 0, n - 1, left, right).first;
        auto& v = pos[cand];
        int cnt = upper_bound(v.begin(), v.end(), right) - lower_bound(v.begin(), v.end(), left);
        return cnt >= threshold ? cand : -1;
    }
};
