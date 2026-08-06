/*
 * @lc app=leetcode id=949 lang=cpp
 *
 * [949] Largest Time For Given Digits
 */
// Translated from 949.largest-time-for-given-digits.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=949 lang=python3
// #
// # [949] Largest Time For Given Digits
// #
// 
// # --- Interview notes (enumerating assignments, validity, total-minutes order, complexity) ---
// #
// # Problem
// # Given **four** digits **`0–9`** (with repetition allowed as multiset counts), arrange them as **`HH:MM`** (24-hour clock). Return the
// # **lexicographically largest valid time string**, which equals **latest chronological time** when interpreted as 24-hour time. If
// # **no** placement yields a valid time, return **`""`**.
// #
// # Validity rules
// # • **Hours `HH`**: **`00`**–**`23`** ⇒ **`10·a + b ∈ [0,23]`** when **`a`** is tens digit, **`b`** ones digit.
// # • **Minutes `MM`**: **`00`**–**`59`** ⇒ **`10·c + d ∈ [0,59]`** for minute tens **`c`** and ones **`d`**.
// #
// # Why brute force over permutations is optimal here
// # Only **`4! = 24`** assignments of the four positions (**`H,H,M,M`**) — trivial constant work. No asymptotic gain from clever pruning
// # beyond micro-optimizations; exhaustive enumeration is **simple**, **correct**, and **interview-safe**.
// #
// # Ordering — compare times by total minutes
// # For valid **`(h, m)`**, **`t = 60·h + m`** is monotone in “clock order”; maximizing **`t`** yields the latest **`HH:MM`**. Format output with
// # **leading zeros**: **`f"{h:02d}:{m:02d}"`**.
// #
// # Algorithm
// # 1. **`itertools.permutations(arr, 4)`** — each **`(a,b,c,d)`** assigns **`HH = ab`**, **`MM = cd`**.
// # 2. **`h = 10a+b`**, **`m = 10c+d`**. If **`h < 24`** and **`m < 60`**, **`t = 60·h+m`**. Track **`best = max(best, t)`**.
// # 3. If **`best`** never updated (**`-1`** sentinel), **`""`**; else format **`best // 60`** and **`best % 60`** with width **2**.
// #
// # Data structures
// # • No heavy structure — optional **`max`** over integer tuples; **`permutations`** is an iterator (**`O(1)`** extra beyond constant stack).
// #
// # Time complexity **`O(4!) = O(1)`** — **24** iterations.
// #
// # Space complexity **`O(1)`** auxiliary (iterator + few integers).
// #
// # Edge cases
// # • **Impossible** — e.g. digits force **`HH ≥ 24`** or **`MM ≥ 60`** for every permutation → **`""`**.
// # • **Leading zeros** — **`00:00`** is valid and may be the answer when all digits zeros.
// #
// # Tests (samples)
// # • **`[1,2,3,4]`** → **`"23:41"`** (latest among valid permutations).
// # • **`[5,5,5,5]`** → **`""`** (minute tens **`5`** ⇒ **`MM ≥ 50`** always fails **`≤ 59`** for required patterns — actually check: only if we get valid — **5555** hour 55 invalid — **`""`**).
// #
// # Improvements
// # • **Early exit** if **`best == 23*60+59`** is impossible with given digits but unnecessary at **24** checks.
// # • **Nested loops** four deep avoid **`itertools`** if forbidden — same complexity.
// #
// # --- end notes ---
// 
// # lc-original code=start
// from itertools import permutations
// from typing import List
// 
// 
// class Solution:
//     def largestTimeFromDigits(self, arr: List[int]) -> str:
//         best = -1
//         for a, b, c, d in permutations(arr):
//             h = 10 * a + b
//             m = 10 * c + d
//             if h < 24 and m < 60:
//                 t = 60 * h + m
//                 if t > best:
//                     best = t
//         if best < 0:
//             return ""
//         return f"{best // 60:02d}:{best % 60:02d}"
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
    string largestTimeFromDigits(vector<int>& arr) {
        sort(arr.begin(), arr.end());
        int best = -1;
        do {
            int h = arr[0] * 10 + arr[1];
            int m = arr[2] * 10 + arr[3];
            if (h < 24 && m < 60) best = max(best, h * 60 + m);
        } while (next_permutation(arr.begin(), arr.end()));
        if (best < 0) return "";
        char buf[6];
        snprintf(buf, sizeof(buf), "%02d:%02d", best / 60, best % 60);
        return string(buf);
    }
};
// @lc code=end
