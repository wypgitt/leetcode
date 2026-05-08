// Translated from 3916.number-of-zig-zag-arrays-iii.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3916 lang=python3
// #
// # [3916] Number of ZigZag Arrays III
// #
// #
// # --- Interview Notes ---------------------------------------------------------
// #
// # Problem restatement
// # We are given n, l, and r. Count arrays a of length n such that:
// #   1. Every value is in the inclusive range [l, r].
// #   2. Adjacent values are never equal.
// #   3. No three consecutive values are strictly increasing.
// #   4. No three consecutive values are strictly decreasing.
// #
// # Since adjacent values cannot be equal, every neighboring pair is either:
// #   up:   a[i] < a[i + 1]
// #   down: a[i] > a[i + 1]
// #
// # Conditions 3 and 4 say we cannot have two equal directions in a row:
// #   up, up     would create a strictly increasing triple
// #   down, down would create a strictly decreasing triple
// #
// # So a valid array must alternate directions:
// #   up, down, up, down, ...
// # or
// #   down, up, down, up, ...
// #
// # We return the count modulo 1_000_000_007.
// #
// #
// # Key normalization
// # The actual values l..r do not matter. Only their relative order matters.
// # Let:
// #   m = r - l + 1
// #
// # Remap the values to:
// #   0, 1, 2, ..., m - 1
// #
// # All comparisons are preserved, so the problem becomes:
// #   count zig-zag arrays of length n using values 0..m-1.
// #
// #
// # Why the previous matrix solution TLEs
// # A natural hard-version solution is matrix exponentiation over the m possible
// # ending values. It works when m is small, but its cost is about O(m^3 log n).
// #
// # The failing test:
// #   n = 13, l = 22, r = 158
// # has:
// #   m = 137
// #
// # Cubic matrix multiplication at m = 137 is already too slow in Python. The
// # intended "III" observation is that the answer is a polynomial in m of degree
// # at most n. Instead of doing work proportional to m^3, we do work proportional
// # to n^2.
// #
// #
// # Standard DP, then the optimization
// # First imagine counting only arrays whose first move is up:
// #   a[0] < a[1] > a[2] < a[3] > ...
// #
// # The first-move-down count is the same by symmetry: replace every value x with
// # m - 1 - x, and up/down are swapped. Therefore:
// #   answer = 2 * first_up_count, for n >= 2
// #
// # A direct endpoint DP would be:
// #   f[x] = number of current arrays ending at value x
// #
// # If the next move is up:
// #   new_f[y] = sum f[x] over x < y
// #
// # If the next move is down:
// #   new_f[y] = sum f[x] over x > y
// #
// # With prefix/suffix sums, that is O(n*m). Still too much when m can be huge.
// #
// #
// # Moment DP with binomial coefficients
// # We avoid storing all f[x]. Instead, store its binomial moments:
// #
// #   B[q] = sum over x of C(x, q) * f[x]
// #
// # where C(x, q) is a binomial coefficient.
// #
// # Why this helps:
// # The transition sums have clean formulas in the binomial basis, thanks to the
// # hockey-stick identity:
// #
// #   sum_{y=0}^{x-1} C(y, q)     = C(x, q + 1)
// #   sum_{y=x+1}^{m-1} C(y, q)   = C(m, q + 1) - C(x + 1, q + 1)
// #   C(x + 1, q + 1)             = C(x, q + 1) + C(x, q)
// #
// # This means each transition can update B without iterating over m values.
// #
// #
// # Base state
// # For length 1 and first-up orientation:
// #   f[x] = 1 for every x in 0..m-1
// #
// # So:
// #   B[q] = sum_{x=0}^{m-1} C(x, q)
// #        = C(m, q + 1)
// #
// # We precompute:
// #   choose_m[t] = C(m, t), for t = 0..n+1
// #
// #
// # Transition formulas
// #
// # 1. Next move is down
// #    new_f[y] = sum_{x > y} f[x]
// #
// #    New moment:
// #      new_B[q]
// #        = sum_y C(y, q) * new_f[y]
// #        = sum_y C(y, q) * sum_{x > y} f[x]
// #        = sum_x f[x] * sum_{y=0}^{x-1} C(y, q)
// #        = sum_x f[x] * C(x, q + 1)
// #        = B[q + 1]
// #
// # 2. Next move is up
// #    new_f[y] = sum_{x < y} f[x]
// #
// #    New moment:
// #      new_B[q]
// #        = sum_y C(y, q) * new_f[y]
// #        = sum_x f[x] * sum_{y=x+1}^{m-1} C(y, q)
// #        = sum_x f[x] * (C(m, q + 1) - C(x + 1, q + 1))
// #        = C(m, q + 1) * B[0] - B[q + 1] - B[q]
// #
// # These two equations are the whole algorithm.
// #
// #
// # Walkthrough of the code
// # 1. Compute m = r - l + 1.
// # 2. If n == 1, return m. There are no adjacent or triple constraints.
// # 3. Precompute C(m, t) modulo MOD for t <= n + 1.
// # 4. Initialize B[q] = C(m, q + 1), the moments for length 1.
// # 5. Perform n - 1 transitions:
// #      step 1 is the first move, which we choose to be up.
// #      step 2 is down.
// #      step 3 is up.
// #      and so on.
// # 6. After all transitions, B[0] is:
// #      sum_x C(x, 0) * f[x] = sum_x f[x]
// #    which is the number of first-up zig-zag arrays.
// # 7. Multiply by 2 for the symmetric first-down arrays.
// #
// #
// # Correctness proof
// #
// # Lemma 1: Every valid array of length at least 2 is either first-up alternating
// # or first-down alternating.
// # Proof:
// # Adjacent values cannot be equal, so each adjacent pair has direction up or down.
// # If two consecutive directions were both up, the corresponding three values would
// # be strictly increasing. If both were down, they would be strictly decreasing.
// # Both are forbidden, so directions must alternate. The first direction is either
// # up or down.
// #
// # Lemma 2: The number of first-up arrays equals the number of first-down arrays.
// # Proof:
// # Map every value x to m - 1 - x. This bijection reverses every comparison, so it
// # transforms first-up arrays into first-down arrays and vice versa.
// #
// # Lemma 3: The initial moments are correct.
// # Proof:
// # At length 1, there is exactly one array ending at each value x, so f[x] = 1.
// # Therefore B[q] = sum C(x, q) over x = 0..m-1. By the hockey-stick identity,
// # that sum is C(m, q + 1).
// #
// # Lemma 4: The down-transition formula new_B[q] = B[q + 1] is correct.
// # Proof:
// # A down move to y can come from any previous value x > y. Switching the order of
// # summation gives:
// #   new_B[q] = sum_x f[x] * sum_{y=0}^{x-1} C(y, q)
// # The inner sum is C(x, q + 1), so new_B[q] = B[q + 1].
// #
// # Lemma 5: The up-transition formula
// #   new_B[q] = C(m, q + 1) * B[0] - B[q + 1] - B[q]
// # is correct.
// # Proof:
// # An up move to y can come from any previous value x < y. Switching the order of
// # summation gives:
// #   new_B[q] = sum_x f[x] * sum_{y=x+1}^{m-1} C(y, q)
// # By hockey-stick:
// #   sum_{y=x+1}^{m-1} C(y, q) = C(m, q + 1) - C(x + 1, q + 1)
// # By Pascal's identity:
// #   C(x + 1, q + 1) = C(x, q + 1) + C(x, q)
// # Substitute into the sum:
// #   new_B[q] = C(m, q + 1) * B[0] - B[q + 1] - B[q]
// #
// # Lemma 6: After each step, B[q] equals the q-th binomial moment of the endpoint
// # distribution for first-up alternating arrays of the current length.
// # Proof:
// # Lemma 3 establishes the base case. Lemma 4 and Lemma 5 show that each legal
// # alternating transition updates all moments exactly. By induction, the invariant
// # holds after every step.
// #
// # Theorem: The algorithm returns the number of valid zig-zag arrays.
// # Proof:
// # By Lemma 6, after n - 1 transitions, B[0] is the total number of first-up arrays
// # because C(x, 0) = 1. By Lemma 1 every valid array is first-up or first-down, and
// # by Lemma 2 the two counts are equal. Therefore 2 * B[0] is exactly the answer
// # for n >= 2. The n == 1 case is handled directly.
// #
// #
// # Complexity analysis
// #
// # Let n be the array length. Notice that m does not appear in the loop bounds.
// #
// # Time:
// #   - Precomputing C(m, t) for t <= n + 1 takes O(n).
// #   - There are n - 1 transitions.
// #   - Transition step s only needs O(n - s + 1) moments.
// #   - Total work is O(n + (n + (n-1) + ... + 1)) = O(n^2).
// #
// # Space:
// #   - choose_m stores O(n) binomial coefficients.
// #   - B stores O(n) moments.
// #   - Each new moment array is O(n), and old arrays are discarded.
// #   Overall space complexity is O(n).
// #
// #
// # Tests to discuss in an interview
// #
// # 1. Official-style examples:
// #      n = 3, l = 4, r = 5 -> 2
// #      n = 3, l = 1, r = 3 -> 10
// #
// # 2. Failing TLE case from submission:
// #      n = 13, l = 22, r = 158 -> 70956316
// #
// # 3. n == 1:
// #      Every single value is valid, so answer = m.
// #
// # 4. n == 2:
// #      Any unequal ordered pair is valid, so answer = m * (m - 1).
// #
// # 5. m == 1:
// #      For n == 1 answer is 1. For n >= 2 answer is 0 because adjacent values
// #      would have to be equal.
// #
// # 6. Small brute force:
// #      For n <= 7 and m <= 6, enumerate all arrays and compare with this solution.
// #      This catches direction parity mistakes and off-by-one errors in binomials.
// #
// #
// # Possible improvements
// #
// # - This O(n^2) moment DP is already much faster than O(m^3 log n) matrix
// #   exponentiation when m is large.
// # - If n were extremely large and m very small, matrix exponentiation can still be
// #   useful. For this hard version, the intended bottleneck is large m, so the
// #   polynomial/moment view is the better default.
// # - Lagrange interpolation is another standard way to use the fact that the answer
// #   is a degree-n polynomial in m. This implementation avoids explicitly
// #   interpolating by updating binomial moments directly.
// #
// # -------------------------------------------------------------------------------
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     MOD = 1_000_000_007
// 
//     def zigZagArrays(self, n: int, l: int, r: int) -> int:
//         mod = self.MOD
//         m = r - l + 1
// 
//         if n == 1:
//             return m % mod
// 
//         choose_m = self._small_binoms(m, n + 1, mod)
// 
//         # Length 1: f[x] = 1, so B[q] = sum_x C(x, q) = C(m, q + 1).
//         moments = [choose_m[q + 1] for q in range(n + 1)]
// 
//         # Count only the orientation whose first move is up:
//         # step 1: up, step 2: down, step 3: up, ...
//         for step in range(1, n):
//             limit = n - step + 1
//             nxt = [0] * limit
// 
//             if step % 2 == 1:
//                 # Up move:
//                 # new_B[q] = C(m, q + 1) * B[0] - B[q + 1] - B[q].
//                 total = moments[0]
//                 for q in range(limit):
//                     nxt[q] = (choose_m[q + 1] * total - moments[q + 1] - moments[q]) % mod
//             else:
//                 # Down move:
//                 # new_B[q] = B[q + 1].
//                 for q in range(limit):
//                     nxt[q] = moments[q + 1]
// 
//             moments = nxt
// 
//         return (2 * moments[0]) % mod
// 
//     def _small_binoms(self, top: int, max_k: int, mod: int) -> List[int]:
//         """Return C(top, k) for k = 0..max_k modulo mod, assuming max_k < mod."""
//         top %= mod
//         inv = [0] * (max_k + 1)
//         if max_k >= 1:
//             inv[1] = 1
//         for x in range(2, max_k + 1):
//             inv[x] = mod - (mod // x) * inv[mod % x] % mod
// 
//         out = [0] * (max_k + 1)
//         out[0] = 1
//         for k in range(1, max_k + 1):
//             out[k] = out[k - 1] * ((top - k + 1) % mod) % mod * inv[k] % mod
//         return out
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
    static constexpr long long MOD = 1000000007LL;

    vector<long long> smallBinoms(long long top, int maxK) {
        top %= MOD;
        vector<long long> inv(maxK + 1), out(maxK + 1);
        if (maxK >= 1) inv[1] = 1;
        for (int x = 2; x <= maxK; ++x) inv[x] = MOD - MOD / x * inv[MOD % x] % MOD;
        out[0] = 1;
        for (int k = 1; k <= maxK; ++k) out[k] = out[k - 1] * ((top - k + 1) % MOD + MOD) % MOD * inv[k] % MOD;
        return out;
    }

public:
    int zigZagArrays(int n, long long l, long long r) {
        long long m = r - l + 1;
        if (n == 1) return m % MOD;
        auto choose = smallBinoms(m, n + 1);
        vector<long long> moments(n + 1);
        for (int q = 0; q <= n; ++q) moments[q] = choose[q + 1];
        for (int step = 1; step < n; ++step) {
            int limit = n - step + 1;
            vector<long long> nxt(limit);
            if (step % 2 == 1) {
                long long total = moments[0];
                for (int q = 0; q < limit; ++q) nxt[q] = (choose[q + 1] * total - moments[q + 1] - moments[q]) % MOD;
            } else {
                for (int q = 0; q < limit; ++q) nxt[q] = moments[q + 1];
            }
            for (auto& x : nxt) x = (x + MOD) % MOD;
            moments.swap(nxt);
        }
        return 2 * moments[0] % MOD;
    }
};
