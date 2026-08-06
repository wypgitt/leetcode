/*
 * @lc app=leetcode id=306 lang=cpp
 *
 * [306] Additive Number
 */
// Translated from 306.additive-number.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=306 lang=python3
// #
// # [306] Additive Number
// #
// 
// # lc-original code=start
// class Solution:
//     pass
// 
// 
// # lc-original code=end
// 
// #
// # lc-original app=leetcode id=306 lang=python3
// #
// # [306] Additive Number
// #
// # =============================================================================
// # INTERVIEW: HOW TO EXPLAIN (elevator → whiteboard)
// # =============================================================================
// #
// # 30 seconds:
// #   "Split the digit string into a Fibonacci-like sequence: after the first two
// #   numbers, each segment must equal the sum of the previous two. I try every
// #   valid split for the first two numbers; once chosen, the rest of the string
// #   is forced — greedily match each next sum left-to-right. Leading zeros are
// #   illegal except for the single digit '0'."
// #
// # 2–4 minutes:
// #   - Brute structure: backtracking could branch heavily; key observation is that
// #     after fixing n1 and n2, every later term is uniquely determined (must equal
// #     n_{k-2}+n_{k-1}), so we only branch on where the first two numbers end.
// #   - Loop split positions: first number num[0:i], second num[i:j]; both must be
// #     valid numeric segments (no multi-digit token starting with '0').
// #   - From position j, repeatedly expect next = add(prev2, prev1) as a decimal
// #     string prefix of the remainder; advance pointer by len(next). Success iff we
// #     consume the whole string and extended beyond j (≥ 3 numbers total).
// #   - Arithmetic: use Python int (arbitrary precision). In languages with 64-bit
// #     limits, use BigInteger or implement schoolbook string addition.
// #
// # =============================================================================
// # ALGORITHM
// # =============================================================================
// #
// # For each i in [1, n-2] (length of first number) and j in [i+1, n-1] (end of
// # second number exclusive):
// #   a = num[0:i], b = num[i:j]
// #   If invalid segment(s), continue.
// #   k = j; x, y = a, b
// #   While k < n:
// #       z = decimal string for int(x) + int(y)   # next Fibonacci term
// #       If num does not have prefix z at k, break.
// #       k += len(z); x, y = y, z
// #   If k == n and k > j, return True   # used at least one term after b
// # Return False
// #
// # =============================================================================
// # DATA STRUCTURES
// # =============================================================================
// #
// # - Only indices into `num` and a few string slices; no auxiliary containers.
// # - Optional: cache int(x) if profiling; not required for LC sizes.
// #
// # =============================================================================
// # COMPLEXITY
// # =============================================================================
// #
// # Let L = len(num). Try O(L^2) pairs (i, j). Verification is O(L) per pair in
// # the worst case (linear scan with possibly growing digit lengths).
// # Overall time O(L^3); space O(L) for slices / recursion stack if any (here O(1)
// # extra besides input).
// #
// # =============================================================================
// # EDGE CASES
// # =============================================================================
// #
// # - Length < 3: cannot form three numbers → False.
// # - Leading zeros: "01", "001" as a segment invalid unless the segment is exactly
// #   "0".
// # - "000": valid as 0 + 0 = 0 (three numbers).
// # - "111": no valid additive split → False.
// # - Large integers: Python int OK; mention BigInteger in Java-style interviews.
// #
// # =============================================================================
// # TESTING
// # =============================================================================
// #
// # Known cases:
// #   - "112358" → True (classic Fibonacci digits).
// #   - "199100199" → True (1, 99, 100, 199).
// #   - "1023" → False.
// # Property: if True, simulate parsing and verify each sum from prior two.
// #
// # =============================================================================
// 
// # lc-original code=start
// class Solution:
//     def isAdditiveNumber(self, num: str) -> bool:
//         """
//         Return True iff `num` can be split into ≥ 3 parts forming an additive
//         sequence (Fibonacci-like), with no illegal leading zeros on segments.
//         """
// 
//         def valid_segment(s: str) -> bool:
//             return len(s) > 0 and (len(s) == 1 or s[0] != "0")
// 
//         n = len(num)
//         if n < 3:
//             return False
// 
//         # Choose end index of first number (exclusive) and second (exclusive).
//         for i in range(1, n - 1):
//             for j in range(i + 1, n):
//                 first = num[:i]
//                 second = num[i:j]
//                 if not valid_segment(first) or not valid_segment(second):
//                     continue
// 
//                 k = j
//                 x, y = first, second
//                 while k < n:
//                     nxt = str(int(x) + int(y))
//                     if k + len(nxt) > n or num[k : k + len(nxt)] != nxt:
//                         break
//                     k += len(nxt)
//                     x, y = y, nxt
// 
//                 # Entire string consumed and we formed at least one term after `second`.
//                 if k == n and k > j:
//                     return True
// 
//         return False
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
    bool valid(const string& s) { return !s.empty() && (s.size() == 1 || s[0] != '0'); }

public:
    bool isAdditiveNumber(string num) {
        int n = num.size();
        if (n < 3) return false;
        for (int i = 1; i < n - 1; ++i) {
            for (int j = i + 1; j < n; ++j) {
                string x = num.substr(0, i), y = num.substr(i, j - i);
                if (!valid(x) || !valid(y)) continue;
                int k = j;
                while (k < n) {
                    string z = add(x, y);
                    if (k + (int)z.size() > n || num.substr(k, z.size()) != z) break;
                    k += z.size();
                    x = y;
                    y = z;
                }
                if (k == n && k > j) return true;
            }
        }
        return false;
    }

    string add(const string& a, const string& b) {
        string res;
        int i = a.size() - 1, j = b.size() - 1, carry = 0;
        while (i >= 0 || j >= 0 || carry) {
            int s = carry;
            if (i >= 0) s += a[i--] - '0';
            if (j >= 0) s += b[j--] - '0';
            res.push_back(char('0' + s % 10));
            carry = s / 10;
        }
        reverse(res.begin(), res.end());
        return res;
    }
};
// @lc code=end
