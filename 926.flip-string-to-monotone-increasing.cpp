// Translated from 926.flip-string-to-monotone-increasing.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=926 lang=python3
// #
// # [926] Flip String To Monotone Increasing
// #
// 
// # --- Interview notes (split point, prefix/suffix costs, one pass, DP variant, complexity) ---
// #
// # Problem
// # **`s`** is a binary string. In one flip you may change **`'0' ↔ '1'`**. Find the **minimum** number of flips so that the string becomes
// # **monotone increasing** in the usual digit order — i.e. there exists an index **`k`** such that every **`'1'`** (if any) appears **not before**
// # every **`'0'`** — equivalently **`s = 0…0 1…1`** (some zeros then some ones).
// #
// # Structural observation — choose a split
// # Any valid monotone binary string is **`0*` followed by `1*`**. So there is a cut **`k ∈ [0, n]`**: positions **`[0, k)`** should become all
// # **`'0'`**, positions **`[k, n)`** should become all **`'1'`**. Overlapping interpretations at **`k`** use empty prefix or empty suffix as needed.
// #
// # Cost for a fixed **`k`**
// # • In **`[0, k)`**, every **`'1'`** must flip → **`#ones(s[0:k])`** flips.
// # • In **`[k, n)`**, every **`'0'`** must flip → **`#zeros(s[k:n])`** flips.
// # Total **`cost(k) = ones_prefix(k) + zeros_suffix(k)`**. The answer is **`min_k cost(k)`**.
// #
// # Why greedy enumeration over **`k`** is enough
// # Only **`n+1`** candidates for **`k`**; each corresponds to a distinct monotone pattern. No fractional optimum — optimal monotone output is
// # fully determined by where zeros end.
// #
// # Algorithm — incremental update (**`O(n)`**, **`O(1)`** space)
// # Maintain **`ones_prefix`** (ones seen so far as **`k`** grows) and **`zeros_suffix`** (zeros remaining in **`s[k:]`**).
// # Initialize **`zeros_suffix = total count of '0' in `s`**`, **`ones_prefix = 0`**. For **`k = 0 … n`**, record **`ones_prefix +
// # zeros_suffix`**, then if **`k < n`**, incorporate **`s[k]`** into the prefix: if **`'1'`** increment **`ones_prefix`**, else decrement
// # **`zeros_suffix`**.
// #
// # Alternative — DP (**`O(n)`** time, can use **`O(n)`** space)
// # **`dp[i][0]`** = min flips for **`s[:i]`** ending with all zeros pattern at **`i`**; **`dp[i][1]`** = min flips ending with ones allowed. Common
// # recurrence matches the same optimum; the split formulation is usually faster to explain in interviews.
// #
// # Data structures
// # **Scalars only** — no arrays required for the optimal solution.
// #
// # Time complexity **`O(n)`** — single pass over **`n+1`** split positions with **`O(1)`** work each.
// #
// # Space complexity **`O(1)`** auxiliary.
// #
// # Edge cases
// # • **`s` all `'0'`** or all **`'1'`** → **`0`** flips.
// # • **`n = 1`** → **`0`**.
// #
// # Tests (LeetCode)
// # • **`"00110"`** → **`1`** (e.g. make **`"00111"`**).
// # • **`"010110"`** → **`2`**.
// # • **`"00011000"`** → **`2`**.
// #
// # Improvements
// # • **Prefix sums** precomputed in arrays — same asymptotics, more cache-friendly for very long strings but unnecessary here.
// #
// # --- end notes ---
// 
// # @lc code=start
// class Solution:
//     def minFlipsMonoIncr(self, s: str) -> int:
//         ones_prefix = 0
//         zeros_suffix = s.count("0")
//         best = float("inf")
//         n = len(s)
//         for k in range(n + 1):
//             best = min(best, ones_prefix + zeros_suffix)
//             if k < n:
//                 if s[k] == "1":
//                     ones_prefix += 1
//                 else:
//                     zeros_suffix -= 1
//         return best
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
    int minFlipsMonoIncr(string s) {
        int ones = 0, zeros = count(s.begin(), s.end(), '0'), best = INT_MAX;
        for (int k = 0; k <= (int)s.size(); ++k) {
            best = min(best, ones + zeros);
            if (k < (int)s.size()) {
                if (s[k] == '1') ++ones;
                else --zeros;
            }
        }
        return best;
    }
};
