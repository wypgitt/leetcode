// Translated from 985.sum-of-even-numbers-after-queries.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=985 lang=python3
// #
// # [985] Sum Of Even Numbers After Queries
// #
// 
// # --- Interview notes (incremental aggregate, parity flip, no full rescan, complexity, edges) ---
// #
// # Problem
// # Integer array **`nums`**. Each query **`[val, index]`** adds **`val`** to **`nums[index]`** (in place). After **each**
// # query, record the **sum of all even values** currently in **`nums`**.
// #
// # Naive approach
// # Recompute **`sum(x for x in nums if x % 2 == 0)`** after every query — **O(n)** per query ⇒ **O(n · q)** total — wasteful when
// # **`q`** and **`n`** are large.
// #
// # Incremental invariant
// # Maintain **`even_sum`** = sum of entries currently even. When **`nums[i]`** changes from **`old`** to **`new = old + val`**:
// # • If **`old`** was even, remove **`old`** from **`even_sum`**.
// # • Update **`nums[i] = new`**.
// # • If **`new`** is even, add **`new`** to **`even_sum`**.
// # Append **`even_sum`** to the answer list each iteration.
// #
// # Parity / negatives (Python)
// # **`x % 2 == 0`** correctly classifies even integers including negatives (`-4 % 2 == 0`).
// #
// # Data structures
// # Only **`nums`** (mutated input), **`even_sum`**, and output list — **no segment trees or fenwick** needed for point updates
// # of this aggregate.
// #
// # Time complexity **O(n + q)`** — initial **O(n)** pass to build **`even_sum`**, then **O(1)** arithmetic per query (**`q`** queries).
// #
// # Space complexity **O(1)** auxiliary excluding output (**`O(q)`** answer length).
// #
// # Edge cases
// # • Query toggles parity multiple times across sequence — incremental updates remain correct.
// # • **`val == 0`** — **`nums[i]`** unchanged; **`even_sum`** unchanged (subtract/add same even value cancels if even).
// #
// # Tests (sanity)
// # • Small custom arrays verify **`even_sum`** matches brute-force sum after each step.
// #
// # Improvements
// # • Bit trick **`x & 1`** for odd test instead of **`% 2`** — micro-optimization only.
// #
// # --- end notes ---
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def sumEvenAfterQueries(self, nums: List[int], queries: List[List[int]]) -> List[int]:
//         even_sum = sum(x for x in nums if x % 2 == 0)
//         ans = []
//         for val, i in queries:
//             if nums[i] % 2 == 0:
//                 even_sum -= nums[i]
//             nums[i] += val
//             if nums[i] % 2 == 0:
//                 even_sum += nums[i]
//             ans.append(even_sum)
//         return ans
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
    vector<int> sumEvenAfterQueries(vector<int>& nums, vector<vector<int>>& queries) {
        int evenSum = 0;
        for (int x : nums) if (x % 2 == 0) evenSum += x;
        vector<int> ans;
        for (auto& q : queries) {
            int val = q[0], i = q[1];
            if (nums[i] % 2 == 0) evenSum -= nums[i];
            nums[i] += val;
            if (nums[i] % 2 == 0) evenSum += nums[i];
            ans.push_back(evenSum);
        }
        return ans;
    }
};
