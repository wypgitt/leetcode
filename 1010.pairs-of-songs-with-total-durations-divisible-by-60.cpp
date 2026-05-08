// Translated from 1010.pairs-of-songs-with-total-durations-divisible-by-60.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=1010 lang=python3
// #
// # [1010] Pairs Of Songs With Total Durations Divisible By 60
// #
// 
// # --- Interview notes (mod 60, complementary remainders, one-pass counting, complexity, edges) ---
// #
// # Problem
// # Count pairs of distinct indices `(i, j)` with `i < j` such that `time[i] + time[j]` is divisible by **60**.
// #
// # Modular reduction
// # Divisibility by 60 depends only on **`time[i] % 60`** and **`time[j] % 60`**. Write **`r = t % 60`** in `{0,…,59}`.
// # Need **`(r_i + r_j) % 60 == 0`**, i.e. **`r_j ≡ -r_i (mod 60)`**, i.e. **`r_j ≡ (60 - r_i) mod 60`**.
// #
// # Why only 60 buckets
// # Remainders partition songs into **60** equivalence classes. Pairing is determined solely by `(remainder, remainder)`:
// # • **`r = 0`** pairs with **`0`** (`0+0 ≡ 0`).
// # • **`r = 30`** pairs with **`30`** (`30+30=60`).
// # • **`r ∈ {1,…,29}`** pairs with **`60 - r`** (e.g. `15` with `45`).
// #
// # One-pass algorithm (ordered pairs `i < j`)
// # Sweep left to right. Maintain **`cnt[r]`** = how many **previous** songs have remainder **`r`**.
// # For current song with remainder **`r`**, every earlier song with remainder **`need = (60 - r) % 60`** completes a valid pair:
// # add **`cnt[need]`** to the answer, then **`cnt[r] += 1`**.
// # This counts each unordered pair exactly once when the **later** index is processed.
// #
// # Why `(60 - r) % 60`**
// # Covers **`r = 0`** (`need = 0`) and **`r = 30`** (`need = 30`) uniformly without branching.
// #
// # Data structure
// # **Fixed array of length 60** — **O(1)** extra space; no hash map needed because keys are bounded.
// #
// # Time complexity **O(n)** — single pass over `time`.
// #
// # Space complexity **O(1)** — `cnt` size 60 is constant.
// #
// # Edge cases
// # • Many copies of same duration — counting handles duplicates; pairs use **distinct indices** via sequential scan.
// # • Duration multiple of 60 — remainder **0**; stacks with other **0** remainders.
// #
// # Tests (typical)
// # • `[30,20,150,100,40]` → **3** (problem example style).
// # • `[60,60,60]` → **3** pairs among three zeros mod 60 (`C(3,2)`).
// #
// # Alternatives
// # • Two-pointer after sorting — **O(n log n)**; worse than remainder DP when only divisibility by 60 matters.
// # • Nested loops — **O(n²)**; fails constraints.
// #
// # --- end notes ---
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def numPairsDivisibleBy60(self, time: List[int]) -> int:
//         cnt = [0] * 60
//         ans = 0
//         for t in time:
//             r = t % 60
//             ans += cnt[(60 - r) % 60]
//             cnt[r] += 1
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
    int numPairsDivisibleBy60(vector<int>& time) {
        vector<int> cnt(60, 0);
        int ans = 0;
        for (int t : time) {
            int r = t % 60;
            ans += cnt[(60 - r) % 60];
            ++cnt[r];
        }
        return ans;
    }
};
