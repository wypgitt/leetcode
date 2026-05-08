// Translated from 3897.maximum-value-of-concatenated-binary-segments.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3897 lang=python3
// #
// # [3897] Maximum Value of Concatenated Binary Segments
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
// # @lc app=leetcode id=3897 lang=python3
// #
// # [3897] Maximum Value of Concatenated Binary Segments
// #
// # --- Notes (problem restatement, greedy sort, value accumulation, complexity) ---
// #
// # Problem restatement
// # Two arrays nums1, nums0 of length n. Segment i is the binary string:
// #   ones^(nums1[i]) followed by zeros^(nums0[i])   i.e. "11..100..0"
// # You may permute the n segments in any order, then concatenate them into one binary
// # string (no separator). Maximize the INTEGER value of that binary number.
// # Return answer modulo 1_000_000_007.
// #
// # Same-length binary comparison
// # For two binary strings of EQUAL length, numeric compare equals LEXICOGRAPHIC compare
// # (both compare MSB first). Here total length m is fixed for any permutation (sum of
// # all segment lengths), so maximizing value equals maximizing lex order as a string.
// #
// # Greedy structure (three kinds of segments)
// # Write segment as S(x,y) = 1^x 0^y with x = nums1[i], y = nums0[i].
// # - Type A (y = 0): only ones — pushing these left puts weight on higher bits without
// #   inserting zeros early. Among type-A blocks, more ones first (compare two all-one
// #   strings of different lengths).
// # - Type B (x > 0 and y > 0): has both runs — earlier segments matter most; putting a
// #   block with more leading 1s earlier dominates; tie-break with FEWER trailing zeros
// #   so we delay switching to the low-value tail.
// # - Type C (x = 0 and y > 0): only zeros — must sit at the RIGHT end (they contribute no
// #   1 bits but occupy higher positions if placed early). Among zero-only blocks, shorter
// #   first frees positions... Official sort uses ascending y among type-C (see comparator).
// #
// # Comparator implemented as sort key (three-tier groups + ties)
// # Group 0: y == 0   -> key (0, -x, 0)   => larger x first among pure-one segments.
// # Group 1: x > 0 and y > 0 -> (1, -x, y) => larger x first; if tie on x, smaller y first.
// # Group 2: x == 0   -> key (2, y, 0)    => pure-zero segments last; ascending y among them.
// # Ordering: group 0 < group 1 < group 2 so pure-one blocks come first, pure-zero last.
// #
// # Pairwise intuition (why local order matches global optimum)
// # Compare concatenating A=S(a,b) vs B=S(c,d). Checking AB vs BA lexicographically gives
// # the same tie-breaking encoded above; sorting by this comparator yields optimal global
// # order for concatenation problems where comparison is "consistent" (standard exchange
// # argument / greedy reorder for multiset of strings under lex-max concatenation with a
// # suitable comparator — contest reduction packages this into the three-type rule).
// #
// # Computing value without building the bit string
// # Let total length m = sum(nums1) + sum(nums0). Precompute pow2[k] = 2^k mod MOD for
// # k = 0..m-1. Scan segments in sorted order. Maintain bit-index `pos` from the MSB:
// # each '1' adds pow2[pos]; each position consumed moves toward less significant bits by
// # decrementing pos. Equivalently: start pos = m-1; for each '1' add pow2[pos]; pos--; for
// # each '0' only pos -= (zeros consume significance slots without adding to the sum).
// #
// # Modular arithmetic
// # All additions use MOD = 10**9 + 7; pow2 built iteratively (p[i] = (p[i-1]*2) % MOD).
// #
// # Time complexity
// # O(n log n + m) — sort n segments; O(m) to fill powers and simulate placing bits.
// # With m <= 2*10^5 from constraints, this is fine.
// #
// # Space complexity
// # O(n + m) for pairs and the power table (m up to 2*10^5).
// #
// # Edge cases
// # - n = 1: sort is trivial; single segment value is (binary value of 1^x 0^y).
// # - y = 0 for all: all type A; order by x descending — all ones string, value 2^m - 1 in
// #   integer terms (mod applied).
// # - x = 0 for a segment: that segment is zeros only; it will be in group 2 at the end.
// # - nums1[i] + nums0[i] > 0: no empty segment.
// #
// # Possible improvements
// # - On-the-fly power: keep running "current weight" w = 2^{pos} mod MOD and update
// #   w = w * inv(2) mod MOD when moving right — needs modular inverse of 2; precompute
// #   pow2 is simpler and O(m) anyway.
// # - For very large m one could use repeated squaring, but m is only 2e5 here.
// #
// # Interview walkthrough
// # 1) Fixed total length => maximize lex order of bit string.
// # 2) Classify segments; sort with the 3-type rule and tie-breaks.
// # 3) Accumulate value with power-of-two weights from MSB to LSB without materializing
// #    the string.
// # 4) State O(n log n + m) time, O(n + m) space, modulo.
// # --- end notes ---
// 
// # @lc code=start
// class Solution:
//     def maxValue(self, nums1: list[int], nums0: list[int]) -> int:
//         MOD = 10**9 + 7
//         pairs = list(zip(nums1, nums0))
//         b = sum(x + y for x, y in pairs)
// 
//         def key(p: tuple[int, int]) -> tuple[int, int, int]:
//             x, y = p
//             if y == 0:
//                 return (0, -x, 0)
//             if x > 0:
//                 return (1, -x, y)
//             return (2, y, 0)
// 
//         pairs.sort(key=key)
// 
//         ans = 0
//         pow2 = [1] * b
//         for i in range(1, b):
//             pow2[i] = pow2[i - 1] * 2 % MOD
// 
//         b -= 1
//         for cnt1, cnt0 in pairs:
//             while cnt1:
//                 ans = (ans + pow2[b]) % MOD
//                 b -= 1
//                 cnt1 -= 1
//             b -= cnt0
//         return ans
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
    int maxValue(vector<int>& nums1, vector<int>& nums0) {
        const long long MOD = 1000000007LL;
        vector<pair<int, int>> pairs;
        int bits = 0;
        for (int i = 0; i < (int)nums1.size(); ++i) {
            pairs.push_back({nums1[i], nums0[i]});
            bits += nums1[i] + nums0[i];
        }
        sort(pairs.begin(), pairs.end(), [](auto a, auto b) {
            auto key = [](pair<int, int> p) {
                int x = p.first, y = p.second;
                if (y == 0) return tuple<int, int, int>{0, -x, 0};
                if (x > 0) return tuple<int, int, int>{1, -x, y};
                return tuple<int, int, int>{2, y, 0};
            };
            return key(a) < key(b);
        });
        vector<long long> pow2(max(1, bits), 1);
        for (int i = 1; i < bits; ++i) pow2[i] = pow2[i - 1] * 2 % MOD;
        long long ans = 0;
        int b = bits - 1;
        for (auto [cnt1, cnt0] : pairs) {
            while (cnt1--) ans = (ans + pow2[b--]) % MOD;
            b -= cnt0;
        }
        return ans;
    }
};
