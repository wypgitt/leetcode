// Translated from 1088.confusing-number-ii.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=1088 lang=python3
// #
// # [1088] Confusing Number II
// #
// 
// # --- Interview notes (definition, digit set, fixed-width enumeration, digit DP, complexity, edges, tests) ---
// #
// # Problem
// # Digits valid under 180° rotation: 0→0, 1→1, 6↔9, 8→8; digits 2,3,4,5,7 are invalid (cannot appear).
// # A positive integer x is a confusing number iff:
// #   (1) every decimal digit of x is valid, and
// #   (2) if we rotate the whole number 180°, interpreting the result as an integer (leading zeros dropped after
// #       rotation), we get a different value than x.
// # Count how many confusing numbers satisfy 1 <= x <= n.
// #
// # Why not iterate 1..n
// # n up to 10^9 — too many candidates.
// #
// # Enumerate only feasible numbers
// # Any confusing number uses only {0,1,6,8,9}. That cuts the search space drastically.
// #
// # Fixed length = len(str(n)) (digit DP / DFS on string of n)
// # Every integer x in [0, n] has a unique representation as exactly L = len(str(n)) digits with allowed leading
// # zeros (e.g. when n = 100, the number 6 is represented as "006"). DFS from the most significant position chooses
// # digits i ∈ [0, up] where up = bound[pos] if still tight to n, else 9 — but skips invalid digits via a map.
// # At depth L we have built integer x; count it if check(x).
// #
// # Rotation check
// # Extract digits of x from least significant to most (standard decimal decomposition). Append mapped digits to y:
// # y = y * 10 + rot[d]. That equals reading the rotated number from the former least-significant side — equivalent
// # to the problem’s 180° reversal rule with leading-zero trimming implicit in integer comparison.
// # Confusing iff x != y (and x used only valid digits — enforced by construction).
// #
// # Why digit DP / DFS instead of BFS generating numbers
// # Same asymptotics for L ≤ 10; DFS plus tight bound matches editorial “Confusing Number II” solutions cleanly.
// #
// # Time complexity
// # At each of L ≤ 10 positions, try up to 5 valid digits with pruning by up → worst-case O(5^L), effectively tiny
// # for L ≤ 10; each leaf does O(L) digit work for check → negligible.
// #
// # Space complexity
// # O(L) recursion stack.
// #
// # Edge cases
// # x = 0 built from all-zero path: check leaves y = 0 → not confusing → contributes 0.
// # Palindromic rotations like 69 vs 96 handled by inequality check.
// # n = 1: only digit choices 0 and 1 → neither confusing → 0.
// #
// # Tests (statement)
// # n = 20 → 6; n = 100 → 19.
// #
// # Improvements
// # - Iterative DP table over position × tight × remainder modulo something — possible but heavier for little gain
// #   at L ≤ 10.
// #
// # --- end notes ---
// 
// # @lc code=start
// class Solution:
//     def confusingNumberII(self, n: int) -> int:
//         # rot[d] = image of digit d after 180° rotation; -1 means invalid in any confusing number
//         rot = [0, 1, -1, -1, -1, -1, 9, -1, 8, 6]
//         s = str(n)
// 
//         def rotated_value(x: int) -> int:
//             y = 0
//             t = x
//             while t:
//                 t, v = divmod(t, 10)
//                 y = y * 10 + rot[v]
//             return y
// 
//         def is_confusing(x: int) -> bool:
//             return x != rotated_value(x)
// 
//         def dfs(pos: int, tight: bool, value: int) -> int:
//             if pos == len(s):
//                 return int(is_confusing(value))
//             limit = int(s[pos]) if tight else 9
//             total = 0
//             for d in range(limit + 1):
//                 if rot[d] == -1:
//                     continue
//                 total += dfs(pos + 1, tight and d == limit, value * 10 + d)
//             return total
// 
//         return dfs(0, True, 0)
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
    int confusingNumberII(int n) {
        vector<int> rot{0, 1, -1, -1, -1, -1, 9, -1, 8, 6};
        string s = to_string(n);
        auto rotated = [&](int x) {
            int y = 0;
            while (x) {
                int v = x % 10;
                x /= 10;
                y = y * 10 + rot[v];
            }
            return y;
        };
        function<int(int, bool, int)> dfs = [&](int pos, bool tight, int value) -> int {
            if (pos == (int)s.size()) return value != rotated(value);
            int limit = tight ? s[pos] - '0' : 9;
            int total = 0;
            for (int d = 0; d <= limit; ++d) {
                if (rot[d] == -1) continue;
                total += dfs(pos + 1, tight && d == limit, value * 10 + d);
            }
            return total;
        };
        return dfs(0, true, 0);
    }
};
