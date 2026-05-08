// Translated from 2719.count-of-integers.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=2719 lang=python3
// #
// # [2719] Count of Integers
// #
// 
// # --- Interview notes (range reduction, digit DP, state, complexity, edges, tests) ---
// #
// # Problem
// # Count integers x with num1 <= x <= num2 (given as decimal strings) such that
// #   min_sum <= digit_sum(x) <= max_sum.
// # Return the count modulo 1_000_000_007.
// #
// # Range reduction (inclusion–exclusion on the upper bound)
// # Let F(N) = # of integers x with 0 <= x <= N and digit sum in [min_sum, max_sum].
// # Then answer = F(num2) - F(num1 - 1)  (all with the same [min_sum, max_sum] filter).
// # Reason: {x : num1 <= x <= num2} = {x : 0 <= x <= num2} \ {x : 0 <= x <= num1-1}.
// # Compute num1 - 1 as a string (big-integer style borrow) so we never convert the full range to int
// # (though Python int would work for |num| <= 1e22, string arithmetic matches interview expectations).
// #
// # Digit DP for F(N)
// # Process the decimal string of N from most significant to least, with:
// #   pos  — current index in the string
// #   s    — sum of digits fixed so far
// #   limit— if True, the prefix so far matches N[0:pos] so the next digit is at most N[pos];
// #          if False, the number is already strictly below N, so the next digit can be 0..9.
// # Transition: try each digit d in 0..up (up = N[pos] if limit else 9), add d to s, propagate limit' = limit and d==N[pos].
// # Base: at pos == len(N), return 1 if min_sum <= s <= max_sum else 0.
// # Leading zeros are allowed, so this counts all x in [0, N] with correct digit sums (shorter numbers correspond to
// # prefixes of zeros, which matches standard “leading zero” digit DP).
// #
// # Memoization
// # Only states with limit=False can be memoized across branches sharing suffix freedom — equivalent to caching all
// # (pos, s, limit); with len(N) <= 23 and s <= 200-ish (23 * 9), state space is tiny.
// #
// # Why not iterate x from num1 to num2
// # Range width can be ~1e22 — impossible.
// #
// # Time complexity
// # O(len · max_sum_state · 10) per F(N); two calls → O(len · max_sum · 10). Here len <= ~23, digit sum in recursion
// # capped by len·9 (≤ 207), well below max_sum constraint 400 for pruning discussion — effectively bounded table size.
// #
// # Space complexity
// # O(len · max_digit_sum) for memo / recursion stack.
// #
// # Edge cases
// # num1 == num1 (single value range): still correct via F(num2) - F(num1-1).
// # num1 == "1": num1 - 1 == "0"; F counts zero (often excluded by min_sum >= 1 in constraints).
// # min_sum <= digit_sum <= max_sum when min_sum > max_sum never happens per constraints.
// #
// # Tests (statement)
// # num1="1", num2="12", min_sum=1, max_sum=8 → 11.
// # num1="1", num2="5", min_sum=1, max_sum=5 → 5.
// #
// # Improvements
// # - Prune recursion when s > max_sum (cannot end in range) to skip work — micro-optimization.
// # - Iterative DP by digit position is possible; memoized DFS is standard in interviews.
// #
// # --- end notes ---
// 
// # @lc code=start
// from functools import cache
// 
// 
// class Solution:
//     def count(self, num1: str, num2: str, min_sum: int, max_sum: int) -> int:
//         mod = 10**9 + 7
// 
//         def sub_one(s: str) -> str:
//             t = list(s)
//             i = len(t) - 1
//             while i >= 0:
//                 if t[i] != "0":
//                     t[i] = chr(ord(t[i]) - 1)
//                     break
//                 t[i] = "9"
//                 i -= 1
//             r = "".join(t).lstrip("0")
//             return r if r else "0"
// 
//         def f(num: str) -> int:
//             @cache
//             def dfs(pos: int, s: int, limit: bool) -> int:
//                 if pos >= len(num):
//                     return int(min_sum <= s <= max_sum)
//                 up = int(num[pos]) if limit else 9
//                 tot = 0
//                 for d in range(up + 1):
//                     if s + d > max_sum:
//                         continue
//                     tot = (tot + dfs(pos + 1, s + d, limit and d == up)) % mod
//                 return tot
// 
//             res = dfs(0, 0, True)
//             dfs.cache_clear()
//             return res
// 
//         return (f(num2) - f(sub_one(num1))) % mod
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
    static constexpr int MOD = 1000000007;
    int minSum, maxSum;

    string subOne(string s) {
        int i = (int)s.size() - 1;
        while (i >= 0) {
            if (s[i] != '0') {
                --s[i];
                break;
            }
            s[i--] = '9';
        }
        size_t p = s.find_first_not_of('0');
        return p == string::npos ? "0" : s.substr(p);
    }

    int countUpTo(const string& num) {
        map<tuple<int, int, bool>, int> memo;
        function<int(int, int, bool)> dfs = [&](int pos, int sum, bool limit) -> int {
            if (pos >= (int)num.size()) return minSum <= sum && sum <= maxSum;
            auto key = make_tuple(pos, sum, limit);
            if (memo.count(key)) return memo[key];
            int up = limit ? num[pos] - '0' : 9;
            long long total = 0;
            for (int d = 0; d <= up; ++d) {
                if (sum + d > maxSum) continue;
                total += dfs(pos + 1, sum + d, limit && d == up);
            }
            return memo[key] = total % MOD;
        };
        return dfs(0, 0, true);
    }

public:
    int count(string num1, string num2, int min_sum, int max_sum) {
        minSum = min_sum;
        maxSum = max_sum;
        return (countUpTo(num2) - countUpTo(subOne(num1)) + MOD) % MOD;
    }
};
