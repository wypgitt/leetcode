/*
 * @lc app=leetcode id=1092 lang=cpp
 *
 * [1092] Shortest Common Supersequence
 */
// Translated from 1092.shortest-common-supersequence.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=1092 lang=python3
// #
// # [1092] Shortest Common Supersequence
// #
// 
// # --- Interview notes (SCS length, LCS DP, backtracking, complexity, edges, tests) ---
// #
// # Problem
// # Return any shortest string T such that str1 and str2 are both subsequences of T.
// #
// # Length formula
// # |SCS(str1, str2)| = |str1| + |str2| − |LCS(str1, str2)|.
// # Reason: start with str1 and str2 concatenated; each character that belongs to a common subsequence was counted
// # twice but should appear once — merging along one longest common subsequence removes exactly |LCS| duplicates.
// #
// # Why compute LCS length first
// # The LCS dynamic-programming table encodes *which* matches are aligned; backtracking from (m, n) to (0, 0)
// # following that table emits characters in an order that realizes one shortest supersequence.
// #
// # LCS DP
// # f[i][j] = LCS length of prefixes str1[:i] and str2[:j].
// #   If str1[i−1] == str2[j−1]: f[i][j] = f[i−1][j−1] + 1.
// #   Else: f[i][j] = max(f[i−1][j], f[i][j−1]).
// #
// # Reconstructing one SCS (walk from (m, n))
// # Think of tracing an optimal path that builds T from right to left (we append to a list then reverse).
// # • If one prefix is exhausted, append the rest of the other string (only one choice).
// # • Otherwise compare f[i][j] with f[i−1][j] and f[i][j−1]:
// #   – If f[i][j] == f[i−1][j]: an optimal LCS alignment does not match str1[i−1] at column j; emit str1[i−1] now and
// #     move to (i−1, j) — that character must still appear in T but is not part of the match at this column.
// #   – Else if f[i][j] == f[i][j−1]: symmetric, emit str2[j−1], move to (i, j−1).
// #   – Else: characters match (diagonal step in LCS); emit that character once and move to (i−1, j−1).
// # When f[i−1][j] == f[i][j−1] (tie), either branch yields a valid shortest supersequence — picking the first rule
// # preserves determinism.
// #
// # Data structures
// # 2D table f with (m+1)×(n+1) ints — fits constraints (≤1001 × 1001).
// # Output built as list of chars then reversed join — O(|str1|+|str2|) characters.
// #
// # Time complexity
// # O(m · n) for DP + O(m + n) backtrack.
// #
// # Space complexity
// # O(m · n) for the table (can be reduced to O(min(m,n)) for LCS length only, but then extra parent bookkeeping is
// # needed to reconstruct — full table is simpler to explain in interviews).
// #
// # Edge cases
// # Identical strings: output equals either string.
// # No common characters: T is str1 + str2 in an order consistent with the walk (effectively interleaving as forced
// # by LCS = 0).
// #
// # Tests (statement)
// # str1 = "abac", str2 = "cab" → one answer is "cabac".
// # str1 = str2 = "aaaaaaaa" → "aaaaaaaa".
// #
// # Improvements
// # - Hirschberg’s algorithm can recover LCS / SCS in O(m·n) time and O(min(m,n)) space — heavier implementation.
// #
// # --- end notes ---
// 
// # lc-original code=start
// class Solution:
//     def shortestCommonSupersequence(self, str1: str, str2: str) -> str:
//         m, n = len(str1), len(str2)
//         f = [[0] * (n + 1) for _ in range(m + 1)]
//         for i in range(1, m + 1):
//             for j in range(1, n + 1):
//                 if str1[i - 1] == str2[j - 1]:
//                     f[i][j] = f[i - 1][j - 1] + 1
//                 else:
//                     f[i][j] = max(f[i - 1][j], f[i][j - 1])
// 
//         ans = []
//         i, j = m, n
//         while i or j:
//             if i == 0:
//                 j -= 1
//                 ans.append(str2[j])
//             elif j == 0:
//                 i -= 1
//                 ans.append(str1[i])
//             else:
//                 if f[i][j] == f[i - 1][j]:
//                     i -= 1
//                     ans.append(str1[i])
//                 elif f[i][j] == f[i][j - 1]:
//                     j -= 1
//                     ans.append(str2[j])
//                 else:
//                     i, j = i - 1, j - 1
//                     ans.append(str1[i])
// 
//         return "".join(ans[::-1])
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
    string shortestCommonSupersequence(string str1, string str2) {
        int m = str1.size(), n = str2.size();
        vector<vector<int>> dp(m + 1, vector<int>(n + 1));
        for (int i = 1; i <= m; ++i) {
            for (int j = 1; j <= n; ++j) {
                if (str1[i - 1] == str2[j - 1]) dp[i][j] = dp[i - 1][j - 1] + 1;
                else dp[i][j] = max(dp[i - 1][j], dp[i][j - 1]);
            }
        }
        string ans;
        int i = m, j = n;
        while (i || j) {
            if (i == 0) ans.push_back(str2[--j]);
            else if (j == 0) ans.push_back(str1[--i]);
            else if (dp[i][j] == dp[i - 1][j]) ans.push_back(str1[--i]);
            else if (dp[i][j] == dp[i][j - 1]) ans.push_back(str2[--j]);
            else {
                --i;
                --j;
                ans.push_back(str1[i]);
            }
        }
        reverse(ans.begin(), ans.end());
        return ans;
    }
};
// @lc code=end
