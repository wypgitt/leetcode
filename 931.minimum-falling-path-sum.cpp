// Translated from 931.minimum-falling-path-sum.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=931 lang=python3
// #
// # [931] Minimum Falling Path Sum
// #
// 
// # --- Interview notes (grid DP, optimal substructure, rolling array, complexity) ---
// #
// # Problem
// # Given an **`n × n`** integer **matrix**, a **falling path** starts in **any** column of the **top** row and moves **down** one row at
// # a time. From **`(i, j)`** the next row may be **`(i+1, j-1)`**, **`(i+1, j)`**, or **`(i+1, j+1)`** (stay in bounds). The **path sum** is
// # the sum of visited cells. Return the **minimum** path sum over all valid falling paths.
// #
// # Optimal substructure
// # Let **`dp[i][j]`** = minimum sum to reach **`(i, j)`** from some start in row **0**. Then
// # **`dp[i][j] = matrix[i][j] + min(dp[i-1][j-1], dp[i-1][j], dp[i-1][j+1])`**, treating out-of-bounds neighbors as **inf** (or only take
// # existing columns). The answer is **`min_j dp[n-1][j]`**.
// #
// # Why dynamic programming
// # The graph of allowed moves is a **layered DAG** (row index always increases), so there are **no cycles**; shortest / min-sum paths
// # satisfy the **Principle of Optimality** — any prefix of a minimum path to **`(i,j)`** is itself minimum to its endpoint. **DP** is
// # natural; **BFS** with weights or **Dijkstra** is overkill for this small local transition.
// #
// # Space optimization
// # Row **`i`** only depends on row **`i-1`**. Two **length-`n`** arrays (**prev**, **cur**) or **one** array updated left-to-right or
// # right-to-left with care — we use **two rows** for clarity (**`O(n)`** space).
// #
// # Data structures
// # **Two `list[int]`** rows — no `heap`, no 2D table required for production space.
// #
// # Time complexity **`O(n²)`** — each of **`n²`** cells, **`O(1)`** work.
// #
// # Space complexity **`O(n)`** auxiliary (**`O(n²)`** if you store full **`dp`** table for reconstruction or debugging).
// #
// # Edge cases
// # • **`n == 1`** — answer is the single cell.
// # • **First row** — **`dp[0][j] = matrix[0][j]`** (or initialize **`prev`** from **`matrix[0]`**).
// #
// # Tests (LeetCode)
// # • **`[[2,1,3],[6,5,4],[7,8,9]]`** → **`13`** (e.g. **1 → 4 → 8**).
// #
// # Improvements
// # • **In-place** on **`matrix`** bottom-up overwrites data — **`O(1)`** extra if mutation allowed.
// # • **Path reconstruction** — keep **`parent` column** or full table.
// #
// # --- end notes ---
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def minFallingPathSum(self, matrix: List[List[int]]) -> int:
//         n = len(matrix)
//         if n == 0:
//             return 0
//         m = len(matrix[0])
//         prev = list(matrix[0])
//         for i in range(1, n):
//             cur = [0] * m
//             for j in range(m):
//                 v = prev[j]
//                 if j > 0:
//                     v = min(v, prev[j - 1])
//                 if j + 1 < m:
//                     v = min(v, prev[j + 1])
//                 cur[j] = matrix[i][j] + v
//             prev = cur
//         return min(prev)
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
    int minFallingPathSum(vector<vector<int>>& matrix) {
        int n = matrix.size();
        if (n == 0) return 0;
        int m = matrix[0].size();
        vector<int> prev = matrix[0];
        for (int i = 1; i < n; ++i) {
            vector<int> cur(m);
            for (int j = 0; j < m; ++j) {
                int v = prev[j];
                if (j > 0) v = min(v, prev[j - 1]);
                if (j + 1 < m) v = min(v, prev[j + 1]);
                cur[j] = matrix[i][j] + v;
            }
            prev.swap(cur);
        }
        return *min_element(prev.begin(), prev.end());
    }
};
