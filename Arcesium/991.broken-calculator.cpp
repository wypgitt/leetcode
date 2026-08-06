/*
 * @lc app=leetcode id=991 lang=cpp
 *
 * [991] Broken Calculator
 */
// Translated from 991.broken-calculator.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=991 lang=python3
// #
// # [991] Broken Calculator
// #
// 
// # --- Interview notes (reverse simulation, greedy halving, parity, complexity, edges) ---
// #
// # Problem
// # Start from integer **`startValue`**. In one operation you may either **`× 2`** or **`- 1`**. Return the **minimum** number
// # of operations to obtain **`target`**.
// #
// # Forward BFS on an infinite graph is impractical (branching state space). **Reverse** the process: start from **`target`** and
// # apply inverse moves toward **`startValue`** until **`target ≤ startValue`**, then finish with **only “increment”** steps in
// # reverse (which are **`- 1`** forward).
// #
// # Inverse operations (undo original moves)
// # • Undo **`× 2`** → **`// 2`** (only when current value is **even** — mirroring that **`× 2`** always produces even numbers).
// # • Undo **`- 1`** → **`+ 1`** (always allowed).
// #
// # Greedy reduction while **`target > startValue`**
// # • If **`target`** is **even**, prefer **`target // 2`**: halving is the inverse of doubling and shrinks toward **`startValue`**
// #   fastest when parity allows (formally optimal for minimizing steps to cross large gaps).
// # • If **`target`** is **odd**, it **cannot** be the immediate result of a **`× 2`** alone (doubling preserves parity from prior
// #   integer — odd **`target`** must have come from **`even − 1`**). So the last forward step was **`- 1`**, i.e. inverse first:
// #   **`target += 1`**, count **one** operation.
// #
// # Terminal phase
// # When **`target ≤ startValue`**, forward moves can only subtract — **`startValue − target`** operations remain (inverse:
// # add **`startValue − target`** to **`target`**), i.e. **`ans += startValue - target`**.
// #
// # Equivalently single line after loop: **`return ans + startValue - target`** with **`target`** possibly reduced below
// # **`startValue`**.
// #
// # Data structures
// # Only integers **`ans`** and **`target`** — **no arrays, heaps, or queues**.
// #
// # Time complexity **O(log target)** halving steps dominate when **`target ≫ startValue`**; odd bumps add **O(1)** overhead each.
// # Worst-case iterations **O(log target + (#odd bumps))** — still polynomially small in bit-length of **`target`**.
// #
// # Space complexity **O(1)**.
// #
// # Edge cases
// # • **`startValue ≥ target`** — loop skipped; answer **`startValue - target`** (only subtract forward).
// # • **`target = 1`** — handled by terminal subtraction unless **`startValue`** already **`1`**.
// #
// # Tests (statement)
// # • **`startValue = 2`, `target = 3`** → **2** (`2 × 2 − 1`).
// # • **`startValue = 5`, `target = 8`** → **2** (`5 − 1`, then `× 2`).
// #
// # Improvements
// # • Bit-tricks / closed forms exist for worst-case patterns — unnecessary for interviews; greedy reverse is standard.
// #
// # --- end notes ---
// 
// # lc-original code=start
// class Solution:
//     def brokenCalc(self, startValue: int, target: int) -> int:
//         ans = 0
//         y = target
//         while y > startValue:
//             ans += 1
//             if y % 2:
//                 y += 1
//             else:
//                 y //= 2
//         return ans + startValue - y
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
    int brokenCalc(int startValue, int target) {
        int ans = 0, y = target;
        while (y > startValue) {
            ++ans;
            if (y % 2) ++y;
            else y /= 2;
        }
        return ans + startValue - y;
    }
};
// @lc code=end
