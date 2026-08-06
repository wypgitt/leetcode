/*
 * @lc app=leetcode id=3890 lang=cpp
 *
 * [3890] Integers With Multiple Sum of Two Cubes
 */
// Translated from 3890.integers-with-multiple-sum-of-two-cubes.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=3890 lang=python3
// #
// # [3890] Integers With Multiple Sum of Two Cubes
// #
// # https://leetcode.com/problems/integers-with-multiple-sum-of-two-cubes/description/
// #
// # algorithms
// # Medium (55.69%)
// # Likes:    48
// # Dislikes: 3
// # Total Accepted:    31.4K
// # Total Submissions: 56.4K
// # Testcase Example:  '4104'
// #
// # You are given an integer n.
// # 
// # An integer x is considered good if there exist at least two distinct pairs
// # (a, b) such that:
// # 
// # 
// # a and b are positive integers.
// # a <= b
// # x = a^3 + b^3
// # 
// # 
// # Return an array containing all good integers less than or equal to n, sorted
// # in ascending order.
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: n = 4104
// # 
// # Output: [1729,4104]
// # 
// # Explanation:
// # 
// # Among integers less than or equal to 4104, the good integers are:
// # 
// # 
// # 1729: 1^3 + 12^3 = 1729 and 9^3 + 10^3 = 1729.
// # 4104: 2^3 + 16^3 = 4104 and 9^3 + 15^3 = 4104.
// # 
// # 
// # Thus, the answer is [1729, 4104].
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: n = 578
// # 
// # Output: []
// # 
// # Explanation:
// # 
// # There are no good integers less than or equal to 578, so the answer is an
// # empty array.
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= n <= 10^9
// # 
// # 
// #
// 
// # lc-original code=start
// class Solution:
//     def findGoodIntegers(self, n: int) -> list[int]:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We need all integers `x <= n` that can be written as:
// 
//             x = a^3 + b^3
// 
//         in at least two distinct ways, where:
// 
//             a and b are positive integers
//             a <= b
// 
//         Example:
// 
//             1729 = 1^3 + 12^3
//                  = 9^3 + 10^3
// 
//         Since it has at least two distinct `(a, b)` pairs, 1729 is good.
// 
//         Key observation: the search space is small
//         ------------------------------------------
//         The constraint looks large:
// 
//             n <= 10^9
// 
//         But we are working with cubes.  If `a^3 + b^3 <= n`, then both `a` and
//         `b` must satisfy:
// 
//             a^3 <= n
//             b^3 <= n
// 
//         So:
// 
//             a <= cube_root(n)
//             b <= cube_root(n)
// 
//         For the maximum possible `n = 10^9`:
// 
//             cube_root(10^9) = 1000
// 
//         That means there are only about:
// 
//             1000 * 1000 / 2 = 500,000
// 
//         pairs with `a <= b`.  Direct enumeration is easily fast enough.
// 
//         Why enumerate pairs instead of numbers?
//         ---------------------------------------
//         A number `x` is good because of how many cube-pair representations it
//         has.  Enumerating every pair `(a, b)` directly produces exactly one
//         representation of exactly one sum.  Then we only need to count how many
//         times each sum appears.
// 
//         Data structure choice
//         ---------------------
//         We use a dictionary:
// 
//             sum_to_count[sum_value] = number of distinct pairs producing it
// 
//         A hash map is ideal because:
// 
//         * insertion/update is O(1) average time
//         * sums are sparse up to 10^9, so an array of size n would be wasteful
//         * we only store sums that are actually produced by cube pairs
// 
//         Algorithm
//         ---------
//         1. Compute `limit = floor(cube_root(n))`.
//         2. Precompute cubes:
// 
//                cubes[i] = i^3
// 
//            for `i = 1..limit`.
// 
//         3. For every pair `a <= b`:
// 
//                total = a^3 + b^3
// 
//            If `total <= n`, increment its count.
//            If `total > n`, break the inner loop, because increasing `b` only
//            makes the sum larger.
// 
//         4. Return all sums whose count is at least 2, sorted increasingly.
// 
//         Computing the cube root safely
//         ------------------------------
//         Floating-point cube roots can be slightly inaccurate around perfect
//         cubes.  Because the limit is small, we can compute the integer cube root
//         with a simple loop:
// 
//             limit = 1
//             while (limit + 1)^3 <= n:
//                 limit += 1
// 
//         This loop runs at most 1000 times under the constraints, so it is both
//         safe and fast.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: Every valid pair `(a, b)` with `a <= b` and
//         `a^3 + b^3 <= n` is considered by the algorithm.
//         Since `a^3 <= a^3 + b^3 <= n` and `b^3 <= a^3 + b^3 <= n`, both `a` and
//         `b` are at most `floor(cube_root(n))`, which is exactly `limit`.  The
//         nested loops visit all pairs with `1 <= a <= b <= limit`, so they visit
//         every valid pair.
// 
//         Lemma 2: The algorithm never misses a valid pair because of the inner
//         `break`.
//         For fixed `a`, the value `a^3 + b^3` strictly increases as `b`
//         increases.  Therefore, once the sum is greater than `n`, all later
//         values of `b` also produce sums greater than `n` and cannot be valid.
// 
//         Lemma 3: For every integer `x <= n`, the dictionary count for `x` equals
//         the number of distinct valid pairs `(a, b)` that produce `x`.
//         By Lemma 1, every valid pair producing `x` is visited and counted.  The
//         loops visit each pair `(a, b)` with `a <= b` exactly once, so no pair is
//         double-counted.  Pairs whose sums exceed `n` are not counted, as required.
// 
//         Theorem: The returned list contains exactly all good integers `<= n`, in
//         ascending order.
//         By definition, an integer is good if at least two distinct valid pairs
//         produce it.  By Lemma 3, this is exactly the condition
//         `sum_to_count[x] >= 2`.  The algorithm returns precisely those keys, and
//         sorts them before returning.
// 
//         Complexity analysis
//         -------------------
//         Let:
// 
//             m = floor(cube_root(n))
// 
//         We enumerate pairs `(a, b)` with `1 <= a <= b <= m`, so there are
//         O(m^2) pairs.  Since `n <= 10^9`, `m <= 1000`.
// 
//         Time:
//             O(m^2 + g log g)
// 
//         where `g` is the number of good integers returned.  The `g log g` term
//         comes from sorting the answer.  Since all sums are generated in pair
//         order rather than numeric order, sorting is the simplest final step.
// 
//         Space:
//             O(u)
// 
//         where `u` is the number of distinct cube sums `<= n`; in the worst case,
//         `u = O(m^2)`.
// 
//         Edge cases
//         ----------
//         * Very small n:
//           If n < 2, even 1^3 + 1^3 is too large, so the answer is empty.
// 
//         * No good integers:
//           We may have many sums, but none with count >= 2.
// 
//         * Perfect cube boundaries:
//           The integer cube-root loop avoids floating-point off-by-one errors.
// 
//         * Pair ordering:
//           We require `a <= b`, so `(1, 12)` and `(12, 1)` are the same
//           representation and should not be counted twice.  Starting `b` from
//           `a` enforces that.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               n = 4104 -> [1729, 4104]
//               n = 578  -> []
// 
//         * First known good value:
//               n = 1728 -> []
//               n = 1729 -> [1729]
// 
//         * Very small values:
//               n = 1 -> []
//               n = 2 -> []
// 
//         * Larger random values:
//           Compare the optimized implementation with a brute-force pair counter
//           over the same cube-root bound.
// 
//         Possible improvement?
//         ---------------------
//         This direct O(cube_root(n)^2) method is already excellent for
//         `n <= 10^9`, because the maximum loop count is roughly 500,000 pairs.
//         A heap-based generation of cube sums is possible, but it adds complexity
//         without improving performance in a meaningful way for these constraints.
//         """
// 
//         limit = 0
//         while (limit + 1) ** 3 <= n:
//             limit += 1
// 
//         cubes = [0] * (limit + 1)
//         for value in range(1, limit + 1):
//             cubes[value] = value ** 3
// 
//         sum_to_count: dict[int, int] = {}
//         for a in range(1, limit + 1):
//             cube_a = cubes[a]
//             for b in range(a, limit + 1):
//                 total = cube_a + cubes[b]
//                 if total > n:
//                     break
//                 sum_to_count[total] = sum_to_count.get(total, 0) + 1
// 
//         return sorted(total for total, count in sum_to_count.items() if count >= 2)
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
    vector<int> findGoodIntegers(int n) {
        int limit = 0;
        while (1LL * (limit + 1) * (limit + 1) * (limit + 1) <= n) ++limit;
        vector<long long> cubes(limit + 1);
        for (int i = 1; i <= limit; ++i) cubes[i] = 1LL * i * i * i;
        map<int, int> count;
        for (int a = 1; a <= limit; ++a) {
            for (int b = a; b <= limit; ++b) {
                long long total = cubes[a] + cubes[b];
                if (total > n) break;
                ++count[(int)total];
            }
        }
        vector<int> ans;
        for (auto [v, c] : count) if (c >= 2) ans.push_back(v);
        return ans;
    }
};
// @lc code=end
