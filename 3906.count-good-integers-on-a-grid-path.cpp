// Translated from 3906.count-good-integers-on-a-grid-path.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3906 lang=python3
// #
// # [3906] Count Good Integers on a Grid Path
// #
// 
// # @lc code=start
// class Solution:
//     pass
// 
// 
// # @lc code=end
// 
// #
// # @lc app=leetcode id=3906 lang=python3
// #
// # [3906] Count Good Integers on a Grid Path
// #
// # --- Notes (problem restatement, digit DP, correctness, complexity, interview) ---
// #
// # Problem restatement
// # Given integers l, r and a string directions of length 6 with exactly three 'D' and
// # three 'R'. For each integer x in [l, r]:
// #   - Pad x to 16 decimal digits with leading zeros (if needed).
// #   - Fill a 4x4 grid in ROW-MAJOR order: indices 0..3 row0, 4..7 row1, ...
// #   - Start at cell (0,0). Apply directions in order: 'D' -> row+1, 'R' -> col+1.
// #     There are 6 moves, so you visit 7 cells total (including start).
// #   - Read the 7 digits along that path in visit order.
// # x is GOOD iff that length-7 digit sequence is NON-DECREASING.
// # Return how many good integers lie in [l, r].
// #
// # Why not brute force over [l, r]?
// # r - l can be on the order of 9e15; iterating every integer is impossible.
// # We need to COUNT valid numbers without enumerating the range.
// #
// # Why digit DP (digit dynamic programming)
// # This is "count numbers in [0, X] satisfying a digit-wise constraint" after fixing the
// # geometry. Classic technique: recursion on digit position with a "tight" flag lim:
// # lim=True means all prefix digits so far equal the upper bound string; then the next
// # digit cannot exceed s[pos]. If we ever go below the bound, lim=False and remaining
// # digits are free 0..9 (subject to other constraints).
// #
// # Grid indices and path order line up with row-major scan
// # Moves are only down/right from (0,0), so each step strictly increases row-major
// # index pos = row*4 + col (down adds 4, right adds 1). Thus the 7 visited cells appear
// # in STRICTLY INCREASING order of pos. When we fill digits left-to-right in pos order
// # (0..15), whenever we hit a cell that lies on the path, that digit must be >= the
// # previous PATH cell's digit. Non-path cells do not appear in the length-7 sequence, so
// # they impose no monotonicity constraint.
// #
// # Precompute key[pos]
// # key[pos] is True iff grid cell pos (row-major) is one of the 7 visited cells.
// # Walk from (0,0), mark key[0]=True, then for each char update (row,col) and set
// # key[row*4+col]=True.
// #
// # DP state
// # dfs(pos, last, lim):
// #   pos  : current digit index 0..15 (processing s[pos]).
// #   last : digit value at the PREVIOUS path cell along the fixed route (in visit order).
// #          Since path indices increase with pos, "previous path cell" is well-defined.
// #   lim  : True iff prefix digits equal bound string s for positions < pos.
// # Start last=0: first path cell digit must be >= 0 (always).
// #
// # Transitions
// # start digit at pos:  last if key[pos] else 0  (path cells must be >= last; others free).
// # end digit at pos:    int(s[pos]) if lim else 9
// # For each digit i in [start, end]:
// #   next_last = i if key[pos] else last
// #   next_lim  = lim and (i == end)
// # Sum dfs(pos+1, next_last, next_lim).
// # Base: pos==16 -> return 1 (one valid completion).
// #
// # Range [l, r]
// # Let F(X) = count of good integers in [0, X]. Answer = F(r) - F(l-1).
// # Handle l==0: calc(l-1)=calc(-1)=0 via guard.
// #
// # Implementation detail (Python caching)
// # The bound string s depends on X; we clear lru_cache between calc calls OR include s in
// # the memo key. Here we use functools.cache and dfs.cache_clear() before each calc(X).
// #
// # Time complexity
// # At most 16 positions, last in 0..9, lim in {True,False}. For lim=False, branching is
// # small; with tight prefix the digit range is limited. Roughly O(16 * 10 * 10) states per
// # bound with memoization; two bounds r and l-1. Often written as O(D * 10 * log10 X) with
// # D=16 fixed -> effectively constant per calc for these constraints.
// #
// # Space complexity
// # Recursion depth O(16); memo table size O(16 * 10 * 2) order; plus bound string length 16.
// #
// # Edge cases
// # - l = r = single value: still two calc calls; difference works.
// # - Leading zeros: zfill(16) ensures exactly 16 digits; small x uses many leading zeros
// #   on path through top-left — Example 1 uses zeros before 8,9,10.
// # - directions always 3D+3R so path stays in grid (contest constraint).
// #
// # Possible improvements
// # - Manual memo[pos][last] when lim is False only (like Java solution) avoids cache_clear.
// # - Pack bound as tuple of ints for cache key to avoid mutating global s.
// #
// # Interview walkthrough
// # 1) Observe range too large to iterate.
// # 2) Fix which 7 grid cells matter (path); note path order matches increasing cell index.
// # 3) Reduce to "count 16-digit strings (with leading zeros) with digit constraints"
// #    -> digit DP with tight bound.
// # 4) Answer F(r)-F(l-1).
// # --- end notes ---
// 
// # @lc code=start
// from functools import cache
// 
// 
// class Solution:
//     def countGoodIntegersOnPath(self, l: int, r: int, directions: str) -> int:
//         key = [False] * 16
//         row, col = 0, 0
//         key[0] = True
//         for c in directions:
//             if c == "D":
//                 row += 1
//             else:
//                 col += 1
//             key[row * 4 + col] = True
// 
//         s = ""
// 
//         @cache
//         def dfs(pos: int, last: int, lim: bool) -> int:
//             if pos == 16:
//                 return 1
// 
//             res = 0
//             start = last if key[pos] else 0
//             end = int(s[pos]) if lim else 9
// 
//             for i in range(start, end + 1):
//                 res += dfs(
//                     pos + 1,
//                     i if key[pos] else last,
//                     lim and (i == end),
//                 )
// 
//             return res
// 
//         def calc(x: int) -> int:
//             nonlocal s
//             if x < 0:
//                 return 0
//             s = str(x).zfill(16)
//             dfs.cache_clear()
//             return dfs(0, 0, True)
// 
//         return calc(r) - calc(l - 1)
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
    vector<int> key;
    string s;
    map<tuple<int, int, bool>, long long> memo;

    long long dfs(int pos, int last, bool lim) {
        if (pos == 16) return 1;
        auto k = make_tuple(pos, last, lim);
        if (memo.count(k)) return memo[k];
        int start = key[pos] ? last : 0;
        int end = lim ? s[pos] - '0' : 9;
        long long res = 0;
        for (int d = start; d <= end; ++d) res += dfs(pos + 1, key[pos] ? d : last, lim && d == end);
        return memo[k] = res;
    }

    long long calc(long long x) {
        if (x < 0) return 0;
        s = to_string(x);
        if (s.size() < 16) s = string(16 - s.size(), '0') + s;
        memo.clear();
        return dfs(0, 0, true);
    }

public:
    long long countGoodIntegersOnPath(long long l, long long r, string directions) {
        key.assign(16, 0);
        int row = 0, col = 0;
        key[0] = 1;
        for (char c : directions) {
            if (c == 'D') ++row;
            else ++col;
            key[row * 4 + col] = 1;
        }
        return calc(r) - calc(l - 1);
    }
};
