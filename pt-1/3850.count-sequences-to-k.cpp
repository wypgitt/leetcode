/*
 * @lc app=leetcode id=3850 lang=cpp
 *
 * [3850] Count Sequences to K
 */
// Translated from 3850.count-sequences-to-k.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=3850 lang=python3
// #
// # [3850] Count Sequences to K
// #
// #
// # --- Interview Notes ---------------------------------------------------------
// #
// # Problem restatement
// # We are given nums and k.
// #
// # Start with:
// #   val = 1
// #
// # For every nums[i], choose exactly one action:
// #   1. multiply val by nums[i]
// #   2. divide val by nums[i]
// #   3. leave val unchanged
// #
// # Division is rational, not integer division, so intermediate values may be
// # fractions. Return the number of distinct action sequences whose final exact
// # rational value equals k.
// #
// # Example:
// #   nums = [2, 3, 2], k = 6
// #
// # Valid choices:
// #   multiply 2, multiply 3, leave 2 -> 6
// #   leave 2, multiply 3, multiply 2 -> 6
// #
// # Answer = 2
// #
// #
// # Key observation: use prime exponents instead of rational values
// # Each nums[i] is between 1 and 6, so its prime factors can only be:
// #   2, 3, 5
// #
// # Every value reachable from val = 1 has the form:
// #   2^a * 3^b * 5^c
// #
// # where a, b, c may be negative because division is allowed.
// #
// # So instead of tracking rational numbers, track the exponent vector:
// #   (a, b, c)
// #
// # Multiplication by x adds x's prime-exponent vector.
// # Division by x subtracts x's prime-exponent vector.
// # Leaving unchanged adds (0, 0, 0).
// #
// # At the end, val == k iff the final exponent vector equals the prime-exponent
// # vector of k.
// #
// #
// # Early impossible case
// # Since nums[i] <= 6, reachable values can only contain prime factors 2, 3, and 5.
// # If k has any other prime factor, no sequence can produce k.
// #
// # Example:
// #   nums = [2, 3, 5], k = 7
// #   Impossible because 7 can never be created.
// #
// #
// # Dynamic programming state
// # Let:
// #   dp[(a, b, c)] = number of action sequences processed so far that produce
// #                   exponent vector (a, b, c)
// #
// # Start:
// #   dp[(0, 0, 0)] = 1
// #
// # For each number x with exponent vector v = (x2, x3, x5), every existing state
// # has three transitions:
// #   leave:    state stays (a, b, c)
// #   multiply: state becomes (a + x2, b + x3, c + x5)
// #   divide:   state becomes (a - x2, b - x3, c - x5)
// #
// # At the end:
// #   answer = dp[target_vector]
// #
// #
// # Why this DP is efficient
// # A naive recursion has 3^n leaves. With n <= 19, that is over one billion in the
// # worst case.
// #
// # But many action sequences lead to the same exponent vector, and the possible
// # exponent ranges are small:
// #   - each nums[i] contributes at most 2 powers of 2, because 4 = 2^2
// #   - at most 1 power of 3
// #   - at most 1 power of 5
// #
// # Across at most 19 numbers, exponent ranges are roughly:
// #   exp2 in [-38, 38]
// #   exp3 in [-19, 19]
// #   exp5 in [-19, 19]
// #
// # This is a small state space, so dictionary DP is clean and fast.
// #
// #
// # Data structure choice
// # We use collections.Counter for dp because:
// #   - keys are exponent triples,
// #   - values are counts of sequences,
// #   - missing states should behave like count 0,
// #   - multiple transitions can add to the same state.
// #
// # A normal dict or defaultdict(int) would also work. Counter is expressive for
// # "count ways to reach each state."
// #
// #
// # Handling nums[i] == 1
// # The prime-exponent vector of 1 is (0, 0, 0).
// #
// # Multiplying by 1, dividing by 1, and leaving unchanged all keep val the same,
// # but they are three distinct action choices. The generic transition code adds
// # the same state three times, so it correctly multiplies the number of ways by 3.
// #
// # Example:
// #   nums = [1, 5], k = 1
// #   The only valid action on 5 is leave.
// #   The action on 1 can be multiply, divide, or leave.
// #   Answer = 3.
// #
// #
// # Walkthrough of the code
// # 1. Factor k using only primes [2, 3, 5].
// # 2. If any factor remains after removing 2, 3, and 5, return 0.
// # 3. Initialize dp with the zero exponent vector.
// # 4. For each nums[i]:
// #      - factor it into a vector,
// #      - create a new Counter,
// #      - apply leave, multiply, and divide transitions from every old state.
// # 5. Return dp[target].
// #
// #
// # Correctness proof
// #
// # Lemma 1: Every reachable rational value has a unique exponent vector over
// # primes 2, 3, and 5.
// # Proof:
// # nums[i] only contains primes 2, 3, and 5. Multiplication adds those prime
// # exponents and division subtracts them. By unique prime factorization, the final
// # rational value is uniquely determined by its exponent vector.
// #
// # Lemma 2: The DP invariant is correct after processing each prefix of nums.
// # Invariant:
// #   dp[state] equals the number of distinct action sequences for the processed
// #   prefix that produce exponent vector state.
// #
// # Proof:
// # Base case: before processing anything, there is exactly one sequence, the empty
// # sequence, and it produces state (0, 0, 0).
// #
// # Inductive step: assume the invariant holds before processing x. For every
// # sequence counted in dp[state], there are exactly three possible next actions:
// # leave, multiply by x, or divide by x. These produce exactly state, state + v,
// # and state - v. The transition adds the old count to exactly those three next
// # states. Therefore the new Counter counts every extended sequence once and only
// # once.
// #
// # Lemma 3: If k has a prime factor outside {2, 3, 5}, the answer is 0.
// # Proof:
// # By Lemma 1, every reachable value only has prime factors 2, 3, and 5. A value
// # containing any other prime factor cannot be reached.
// #
// # Theorem: The algorithm returns the number of action sequences that end at k.
// # Proof:
// # If k has another prime factor, Lemma 3 proves returning 0 is correct.
// # Otherwise k has a target exponent vector. By Lemma 2, after all nums are
// # processed, dp[target] is exactly the number of action sequences whose final
// # exponent vector equals target. By Lemma 1, that is exactly the number of
// # sequences whose final rational value equals k.
// #
// #
// # Complexity analysis
// #
// # Let n = len(nums), and let S be the number of distinct exponent vectors reached.
// #
// # Time:
// #   For each number, we iterate over all current states and perform 3 O(1)
// #   transitions.
// #   Time complexity is O(n * S).
// #
// # With the constraints:
// #   exp2 has at most 77 possible values,
// #   exp3 has at most 39 possible values,
// #   exp5 has at most 39 possible values,
// # so S is bounded by about 77 * 39 * 39, and in practice much smaller.
// #
// # Space:
// #   We store the current DP map and the next DP map.
// #   Space complexity is O(S).
// #
// #
// # Tests to discuss in an interview
// #
// # 1. Example 1:
// #      nums = [2, 3, 2], k = 6 -> 2
// #
// # 2. Example 2:
// #      nums = [4, 6, 3], k = 2 -> 2
// #
// # 3. nums[i] == 1 creates distinct no-op actions:
// #      nums = [1, 5], k = 1 -> 3
// #
// # 4. Impossible prime factor:
// #      nums = [2, 3, 5], k = 7 -> 0
// #
// # 5. k = 1:
// #      Need final exponent vector (0, 0, 0). Multiplications and divisions can
// #      cancel each other.
// #
// # 6. All ones:
// #      nums = [1, 1, 1], k = 1 -> 3^3 = 27
// #
// # 7. Randomized brute force:
// #      For small n, enumerate all 3^n action sequences using Fraction and compare
// #      with this DP. This validates rational division behavior.
// #
// #
// # Edge cases
// #
// # - nums length 1: exactly check multiply, divide, and leave.
// # - k is huge: factoring only by 2, 3, and 5 is still O(log k).
// # - Division creates negative exponents: tuples naturally support negative values.
// # - No modulo is requested: return the exact count. The maximum number of
// #   sequences is 3^19, which is easily handled by Python int.
// #
// #
// # Possible improvements
// #
// # - Meet-in-the-middle is also valid: enumerate 3^(n/2) exponent vectors for each
// #   half and match complements. With n <= 19, both approaches pass.
// # - DP is often easier to explain because it directly mirrors the three choices
// #   at every index and automatically merges equivalent rational states.
// # - If nums[i] had larger prime factors, we would factor all relevant primes from
// #   nums and k. Here the fixed bound nums[i] <= 6 lets us hardcode [2, 3, 5].
// #
// # -------------------------------------------------------------------------------
// 
// # lc-original code=start
// from collections import Counter
// from typing import List, Tuple
// 
// 
// class Solution:
//     def countSequences(self, nums: List[int], k: int) -> int:
//         target, reachable = self._factor_target(k)
//         if not reachable:
//             return 0
// 
//         dp = Counter({(0, 0, 0): 1})
// 
//         for num in nums:
//             da, db, dc = self._factor_small(num)
//             nxt = Counter()
// 
//             for (a, b, c), ways in dp.items():
//                 nxt[(a, b, c)] += ways
//                 nxt[(a + da, b + db, c + dc)] += ways
//                 nxt[(a - da, b - db, c - dc)] += ways
// 
//             dp = nxt
// 
//         return dp[target]
// 
//     def _factor_target(self, value: int) -> Tuple[Tuple[int, int, int], bool]:
//         exponents = []
//         for prime in (2, 3, 5):
//             count = 0
//             while value % prime == 0:
//                 value //= prime
//                 count += 1
//             exponents.append(count)
//         return (exponents[0], exponents[1], exponents[2]), value == 1
// 
//     def _factor_small(self, value: int) -> Tuple[int, int, int]:
//         exponents = []
//         for prime in (2, 3, 5):
//             count = 0
//             while value % prime == 0:
//                 value //= prime
//                 count += 1
//             exponents.append(count)
//         return exponents[0], exponents[1], exponents[2]
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
    pair<array<int, 3>, bool> factorTarget(int value) {
        array<int, 3> exps{};
        int primes[3] = {2, 3, 5};
        for (int i = 0; i < 3; ++i) while (value % primes[i] == 0) {
            value /= primes[i];
            ++exps[i];
        }
        return {exps, value == 1};
    }
    array<int, 3> factorSmall(int value) {
        array<int, 3> exps{};
        int primes[3] = {2, 3, 5};
        for (int i = 0; i < 3; ++i) while (value % primes[i] == 0) {
            value /= primes[i];
            ++exps[i];
        }
        return exps;
    }

public:
    long long countSequences(vector<int>& nums, int k) {
        auto [target, ok] = factorTarget(k);
        if (!ok) return 0;
        map<array<int, 3>, long long> dp;
        dp[{0, 0, 0}] = 1;
        for (int num : nums) {
            auto d = factorSmall(num);
            map<array<int, 3>, long long> nxt;
            for (auto& [state, ways] : dp) {
                nxt[state] += ways;
                nxt[{state[0] + d[0], state[1] + d[1], state[2] + d[2]}] += ways;
                nxt[{state[0] - d[0], state[1] - d[1], state[2] - d[2]}] += ways;
            }
            dp.swap(nxt);
        }
        return dp[target];
    }
};
// @lc code=end
