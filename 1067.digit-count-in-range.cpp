/*
 * @lc app=leetcode id=1067 lang=cpp
 *
 * [1067] Digit Count in Range
 */
// Translated from 1067.digit-count-in-range.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=1067 lang=python3
// #
// # [1067] Digit Count in Range
// #
// 
// # --- Interview notes (range reduction, digit DP state machine, leading zeros, complexity, edges, tests) ---
// #
// # Problem
// # Given digit d ∈ [0,9] and integers low ≤ high, count how many times digit d appears in the decimal writing of
// # all integers x with low ≤ x ≤ high (count multiplicity per integer, e.g. 11 contributes two 1’s).
// #
// # Range reduction
// # Let F(N) = total occurrences of digit d in all integers x with 0 ≤ x ≤ N (decimal, no leading zeros except the
// # number 0 itself handled via leading-zero mechanics).
// # Answer = F(high) − F(low − 1).
// #
// # Why digit DP instead of iterating [low, high]
// # high − low can be ~2·10^8 — scanning every integer is too slow.
// #
// # Digit DP model (count occurrences, not count numbers)
// # Decompose N into digits a[1..L] with a[1] = least significant digit (editorial indexing). DFS processes from
// # position L down to 1 (most significant → least).
// # State:
// #   pos   — next digit position to fix.
// #   cnt   — how many copies of digit d have been placed so far on this path.
// #   lead  — still placing leading zeros before the number truly starts (important when d = 0).
// #   limit — tight to prefix of N (cannot exceed N).
// # Transition: try digit i ∈ [0, up] where up = a[pos] if limit else 9.
// #   • If i == 0 and lead: still “no real digit yet” → recurse with lead True (still flexible), cnt unchanged.
// #   • Else the number has started; count += 1 if i == d; lead becomes False.
// # Base pos ≤ 0: return cnt.
// #
// # Memoization
// # Python functools.cache on dfs; states bounded by pos ≤ 10, cnt ≤ 10, booleans — tiny graph.
// # (Java editorial memoizes only when ¬lead ∧ ¬limit for speed; cache-all is fine here.)
// #
// # Special role of digit 0
// # Leading zeros before the first non-zero digit must not be counted as occurrences of ‘0’ (otherwise every
// # shorter-length padding would inflate zeros). The lead flag suppresses those.
// #
// # Time complexity
// # O(log10 N) positions × O(10) digit choices × memo hits → effectively O(log N) per F(N), two calls total.
// #
// # Space complexity
// # O(log N) recursion depth + memo table negligible.
// #
// # Alternative (mention only)
// # Closed-form digit enumeration (“rotate factor” method from CS interviews) counts occurrences in O(log N)
// # without recursion — useful when memo limits matter; digit DP is easier to derive under pressure.
// #
// # Edge cases
// # low = 1 ⇒ low − 1 = 0 ⇒ F(0) = 0 with our extraction loop (no digits → dfs returns 0 immediately).
// # d = 0 needs correct leading-zero handling (validated via brute tests).
// #
// # Tests (statement)
// # d = 1, low = 1, high = 13 → 6.
// # d = 3, low = 100, high = 250 → 35.
// #
// # Improvements
// # - Iterative DP table instead of recursion if stack depth ever matters (not here).
// #
// # --- end notes ---
// 
// # lc-original code=start
// from functools import cache
// 
// 
// class Solution:
//     def digitsCount(self, d: int, low: int, high: int) -> int:
//         def upto(n: int) -> int:
//             if n < 0:
//                 return 0
//             a = [0] * 11
//             l = 0
//             t = n
//             while t > 0:
//                 l += 1
//                 a[l] = t % 10
//                 t //= 10
// 
//             @cache
//             def dfs(pos: int, cnt: int, lead: bool, limit: bool) -> int:
//                 if pos <= 0:
//                     return cnt
//                 up = a[pos] if limit else 9
//                 total = 0
//                 for i in range(up + 1):
//                     if i == 0 and lead:
//                         total += dfs(pos - 1, cnt, True, limit and i == up)
//                     else:
//                         total += dfs(
//                             pos - 1,
//                             cnt + (1 if i == d else 0),
//                             False,
//                             limit and i == up,
//                         )
//                 return total
// 
//             return dfs(l, 0, True, True)
// 
//         return upto(high) - upto(low - 1)
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
    int digit;

    long long upto(int n) {
        if (n < 0) return 0;
        vector<int> a(11, 0);
        int len = 0;
        for (int t = n; t > 0; t /= 10) a[++len] = t % 10;
        map<tuple<int, int, bool, bool>, long long> memo;
        function<long long(int, int, bool, bool)> dfs = [&](int pos, int cnt, bool lead, bool limit) -> long long {
            if (pos <= 0) return cnt;
            auto key = make_tuple(pos, cnt, lead, limit);
            if (memo.count(key)) return memo[key];
            int up = limit ? a[pos] : 9;
            long long total = 0;
            for (int x = 0; x <= up; ++x) {
                if (x == 0 && lead) total += dfs(pos - 1, cnt, true, limit && x == up);
                else total += dfs(pos - 1, cnt + (x == digit), false, limit && x == up);
            }
            return memo[key] = total;
        };
        return dfs(len, 0, true, true);
    }

public:
    int digitsCount(int d, int low, int high) {
        digit = d;
        return (int)(upto(high) - upto(low - 1));
    }
};
// @lc code=end
