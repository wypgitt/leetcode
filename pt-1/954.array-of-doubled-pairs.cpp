/*
 * @lc app=leetcode id=954 lang=cpp
 *
 * [954] Array Of Doubled Pairs
 */
// Translated from 954.array-of-doubled-pairs.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=954 lang=python3
// #
// # [954] Array Of Doubled Pairs
// #
// 
// # --- Interview notes (pair `(x, 2x)`, greedy order by `|x|`, Counter, complexity) ---
// #
// # Problem
// # **`arr`** has **even** length. Return **`True`** iff we can **reorder** into **`seq`** such that for every **`k`** in **`[0, n/2)`**,
// # **`seq[2k+1] = 2 · seq[2k]`** — partition into **`n/2`** pairs **`(x, 2x)`**, multiset preserved.
// #
// # Multiset view
// # Each **`x`** uses one copy of **`x`** and one copy of **`2x`**, except **`0`** which pairs with **`0`**. So we need **`count(0)`**
// # **even**, and for **`x ≠ 0`** we consume **`count[x]`** copies from **`count[2x]`** after processing **`x`** as the “smaller half” of
// # the pair in the **`|·|`** ordering below.
// #
// # Greedy order — sort keys by **`abs(x)`** ascending
// # • **Positive:** **`2x > x`**. Process **small** values first so **`2`** is still available when pairing **`1`**, not consumed as the
// #   leading **`x`** for a **`(2,4)`** chain incorrectly.
// # • **Negative:** **`2x < x`** (more negative). The partner **`2x`** **precedes** **`x`** in normal numeric order but has **larger**
// #   **`|·|`**. Processing **`|x|`** ascending visits **`-4`** before **`-8`**, matching **`-4`** with **`-8`** correctly.
// # • **Ties on **`|x|`**:** Python’s sort uses **`key=abs`** then breaks ties by **value** — **`-4`** before **`4`**, which avoids mixing
// #   opposite-sign chains incorrectly when **`|a|`** matches.
// #
// # Algorithm
// # 1. **`Counter(arr)`**.
// # 2. If **`count[0]`** is **odd** → **`False`**.
// # 3. For **`x`** in **`sorted(count.keys(), key=abs)`** (skip if **`count[x] == 0`** after earlier steps):
// #    **`y = 2x`**. If **`count[y] < count[x]`** → **`False`**. Else **`count[y] -= count[x]`** (and implicitly **`count[x]`** becomes unused —
// #    zero after subtraction from **`y`** when **`x`** was “leading”; matching editorial **`freq[2x] -= freq[x]`** pattern).
// # 4. **`True`** if no failure.
// #
// # Implementation detail
// # Editorial pattern **`freq[2*k] -= freq[k]`** zeros **`k`**’s contribution by pulling from **`2k`**’s bucket (same as “pair **`k`**
// # with **`2k`**”). Skip **`freq[k] == 0`** when **`k`** was fully consumed indirectly — otherwise **`freq[2k] < freq[k]`** can misfire on
// # stale keys; **`continue`** when **`cnt[x]==0`** is safe.
// #
// # Data structures
// # **`collections.Counter`** — **`O(n)`** frequencies.
// #
// # Time complexity **`O(n log n)`** — sorting **`≤ n`** distinct keys.
// #
// # Space complexity **`O(n)`**.
// #
// # Edge cases
// # • **`[0,0]`** → **`True`**; **`[0,0,0,0]`** → **`True`**; odd number of zeros → **`False`** (handled by parity check).
// #
// # Tests (LeetCode)
// # • **`[3,1,3,6]`** → **`False`**.
// # • **`[2,1,2,6]`** → **`False`**.
// # • **`[4,-2,2,-4]`** → **`True`** (e.g. **`[-2,-4,2,4]`**).
// #
// # Improvements
// # • **`sorted(keys, key=abs)`** matches official solutions; **`key=lambda z: (abs(z), z)`** is equivalent for typical tie-breaking.
// #
// # --- end notes ---
// 
// # lc-original code=start
// from collections import Counter
// from typing import List
// 
// 
// class Solution:
//     def canReorderDoubled(self, arr: List[int]) -> bool:
//         cnt = Counter(arr)
//         if cnt[0] % 2:
//             return False
// 
//         for x in sorted(cnt.keys(), key=abs):
//             if cnt[x] == 0:
//                 continue
//             y = 2 * x
//             if cnt[y] < cnt[x]:
//                 return False
//             cnt[y] -= cnt[x]
// 
//         return True
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
    bool canReorderDoubled(vector<int>& arr) {
        map<int, int> cnt;
        for (int x : arr) ++cnt[x];
        if (cnt[0] % 2) return false;
        vector<int> keys;
        for (auto [x, _] : cnt) keys.push_back(x);
        sort(keys.begin(), keys.end(), [](int a, int b) { return abs(a) < abs(b); });
        for (int x : keys) {
            if (cnt[x] == 0) continue;
            int y = 2 * x;
            if (cnt[y] < cnt[x]) return false;
            cnt[y] -= cnt[x];
        }
        return true;
    }
};
// @lc code=end
