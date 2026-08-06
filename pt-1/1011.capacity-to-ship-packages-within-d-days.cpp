/*
 * @lc app=leetcode id=1011 lang=cpp
 *
 * [1011] Capacity To Ship Packages Within D Days
 */
// Translated from 1011.capacity-to-ship-packages-within-d-days.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=1011 lang=python3
// #
// # [1011] Capacity To Ship Packages Within D Days
// #
// 
// # --- Interview notes (monotone feasibility, binary search on answer, greedy packing, complexity, edges) ---
// #
// # Problem
// # Packages have weights `weights[i]` and **must be shipped in given order** (no reordering). Each day you load a **prefix
// # of the remaining** packages onto one ship until adding the **next** package would exceed the ship’s capacity limit **`W`**
// # (or you’ve shipped everything). Find the **minimum integer capacity `W`** such that all packages can be shipped within
// # **`days`** calendar days.
// #
// # Search space for `W`
// # • **Lower bound:** `max(weights)` — a single package cannot be split; the ship must hold the heaviest item alone.
// # • **Upper bound:** `sum(weights)` — load everything in one day (always schedule-feasible if `days >= 1`).
// # Optimal `W` lies in **`[max(weights), sum(weights)]`**.
// #
// # Monotonicity — why binary search works
// # If capacity **`W`** works (exists a valid packing into ≤ `days` days), then any **`W' ≥ W`** also works (same packing fits;
// # extra slack only helps). If **`W`** fails, any **`W' < W`** fails too. So feasibility is **monotone** in **`W`** ⇒ binary
// # search the **smallest** feasible capacity.
// #
// # Feasibility check `can(W)` — greedy in **O(n)**
// # Simulate shipping in order: accumulate weight on the current day; when adding the next package would exceed **`W`**, close
// # the day (`need_days += 1`, start new load with that package). If **`need_days > days`**, return **False**; else **True**.
// # Greedy is optimal for fixed **`W`**: any partition into contiguous segments with segment sums ≤ **`W`** uses at least this
// # many days (you pack each day as heavy as possible without exceeding **`W`**).
// #
// # Algorithm
// # Binary search **`lo = max(weights)`**, **`hi = sum(weights)`**. Mid **`mid`**: if **`can(mid)`** then **`hi = mid`** else
// # **`lo = mid + 1`**. Terminate **`lo == hi`** → answer.
// #
// # Data structures
// # Only integers and a linear scan — **no auxiliary arrays** beyond loop variables.
// #
// # Time complexity **O(n · log(S))** where **`S = sum(weights)`** (search range); **`n = len(weights)`** per feasibility check.
// #
// # Space complexity **O(1)** extra.
// #
// # Edge cases
// # • **`days == len(weights)`** — each package its own day → answer **`max(weights)`**.
// # • **`days == 1`** — answer **`sum(weights)`**.
// #
// # Tests (statement-style)
// # • `weights = [1,2,3,4,5,6,7,8,9,10]`, `days = 5` → **15** (example from problem discussions).
// # • `weights = [3,2,2,4,1,4]`, `days = 3` → **6**.
// #
// # Improvements
// # • Upper bound can be tightened (e.g. binary search on sorted prefix sums) — rarely needed; **`sum(weights)`** is standard.
// # • For very large **`S`**, bounds use Python integers transparently.
// #
// # --- end notes ---
// 
// # lc-original code=start
// from typing import List
// 
// 
// class Solution:
//     def shipWithinDays(self, weights: List[int], days: int) -> int:
//         def can(cap: int) -> bool:
//             need = 1
//             cur = 0
//             for w in weights:
//                 if cur + w > cap:
//                     need += 1
//                     cur = w
//                 else:
//                     cur += w
//                 if need > days:
//                     return False
//             return True
// 
//         lo, hi = max(weights), sum(weights)
//         while lo < hi:
//             mid = (lo + hi) // 2
//             if can(mid):
//                 hi = mid
//             else:
//                 lo = mid + 1
//         return lo
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
public:
    int shipWithinDays(vector<int>& weights, int days) {
        auto can = [&](int cap) {
            int need = 1, cur = 0;
            for (int w : weights) {
                if (cur + w > cap) {
                    ++need;
                    cur = w;
                } else {
                    cur += w;
                }
                if (need > days) return false;
            }
            return true;
        };
        int lo = *max_element(weights.begin(), weights.end());
        int hi = accumulate(weights.begin(), weights.end(), 0);
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (can(mid)) hi = mid;
            else lo = mid + 1;
        }
        return lo;
    }
};
// @lc code=end
