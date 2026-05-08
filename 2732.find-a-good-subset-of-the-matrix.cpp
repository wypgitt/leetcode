// Translated from 2732.find-a-good-subset-of-the-matrix.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=2732 lang=python3
// #
// # [2732] Find a Good Subset of the Matrix
// #
// 
// # --- Interview notes (condition, bit trick, why only k=1 or 2, complexity, edges, tests) ---
// #
// # Problem
// # Binary matrix m × n. Choose a non-empty subset of rows of size k. Let column sums be c_j.
// # Require c_j <= floor(k / 2) for every column j.
// # Return any sorted list of chosen row indices, or [] if impossible.
// #
// # Column semantics as bits
// # Row i is a length-n bit pattern (n <= 5). Pack row into mask r_i ∈ [0, 2^n): bit j is grid[i][j].
// #
// # k = 1
// # floor(1/2) = 0 ⇒ every column sum must be 0 ⇒ the row must be all zeros ⇒ mask == 0.
// #
// # k = 2
// # floor(2/2) = 1 ⇒ each column sum ≤ 1 ⇒ no column may have two 1s ⇒ the two rows cannot both have a 1 in the
// # same column ⇒ bitwise AND of their masks must be 0.
// #
// # Why larger k never helps (given n <= 5)
// # - Odd k ≥ 3: floor(k/2) is still 1 (for k=3), same per-column cap as k=2. Any three rows contain a pair;
// #   if no pair is disjoint (AND=0), triple cannot satisfy column sums ≤1 — editorial argues failure of k=2
// #   implies failure for odd k>1.
// # - Even k ≥ 4: floor(k/2) ≥ 2. Among any 4 distinct rows, there are C(4,2)=6 column pairs that could both be 1;
// #   pushing sums above 2 forces some column sum ≥3 when n≤5 (pigeonhole / averaging argument in editorial).
// # Therefore only k ∈ {1, 2} need to be checked.
// #
// # Algorithm
// # 1. Scan rows; build mask per row. If mask == 0, immediately return [row_index].
// # 2. Store map mask → row index (one representative index per distinct mask is enough: pairing masks A and B
// #    only needs any row realizing A and any row realizing B).
// # 3. For every pair of entries (a, i), (b, j) in the map, if (a & b) == 0, return sorted([i, j]).
// # 4. Return [].
// #
// # Data structures
// # - Dictionary / hash map from mask (int) to first-seen row index: O(2^n) distinct masks at most (here ≤ 32).
// # - Bit operations for AND / packing row into mask.
// #
// # Time complexity
// # O(m · n) to build masks + O(U^2) over distinct masks U ≤ 2^n ≤ 32 ⇒ effectively O(m · n + 4^n) with tiny constant.
// #
// # Space complexity
// # O(U) for the map, O(1) besides input if masks streamed — here O(min(m, 2^n)) entries.
// #
// # Edge cases
// # - Single cell [[0]]: mask 0 ⇒ [0].
// # - Single cell [[1]]: no all-zero row; pairs need AND 0 — impossible with one row ⇒ []... Actually one row k=1:
// #   need mask 0, [[1]] fails ⇒ [].
// # - Duplicate identical rows: map keeps one index; pairing still finds disjoint masks from other rows if they exist.
// #
// # Tests (statement)
// # Example 1 → [0,1]; Example 2 → [0]; Example 3 → [].
// #
// # Improvements
// # - Iterate masks only up to 2^n without scanning all rows twice — current solution is already optimal order for
// #   constraints.
// #
// # --- end notes ---
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def goodSubsetofBinaryMatrix(self, grid: List[List[int]]) -> List[int]:
//         first = {}
//         for i, row in enumerate(grid):
//             mask = 0
//             for j, x in enumerate(row):
//                 mask |= x << j
//             if mask == 0:
//                 return [i]
//             first[mask] = i
// 
//         for a, i in first.items():
//             for b, j in first.items():
//                 if (a & b) == 0:
//                     return [i, j] if i < j else [j, i]
// 
//         return []
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
    vector<int> goodSubsetofBinaryMatrix(vector<vector<int>>& grid) {
        unordered_map<int, int> first;
        for (int i = 0; i < (int)grid.size(); ++i) {
            int mask = 0;
            for (int j = 0; j < (int)grid[i].size(); ++j) mask |= grid[i][j] << j;
            if (mask == 0) return {i};
            first[mask] = i;
        }
        for (auto [a, i] : first) for (auto [b, j] : first) if ((a & b) == 0) {
            if (i < j) return {i, j};
            return {j, i};
        }
        return {};
    }
};
