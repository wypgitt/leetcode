#
# @lc app=leetcode id=3896 lang=python3
#
# [3896] Minimum Operations to Transform Array into Alternating Prime
#
# https://leetcode.com/problems/minimum-operations-to-transform-array-into-alternating-prime/description/
#
# algorithms
# Medium (53.01%)
# Likes:    59
# Dislikes: 4
# Total Accepted:    32.4K
# Total Submissions: 61K
# Testcase Example:  '[1,2,3,4]'
#
# You are given an integer array nums.
# 
# An array is considered alternating prime if:
# 
# 
# Elements at even indices (0-based) are prime numbers.
# Elements at odd indices are non-prime numbers.
# 
# 
# In one operation, you may increment any element by 1.
# 
# Return the minimum number of operations required to transform nums into an
# alternating prime array.
# 
# A prime number is a natural number greater than 1 with only two factors, 1
# and itself.
# 
# 
# Example 1:
# 
# 
# Input: nums = [1,2,3,4]
# 
# Output: 3
# 
# Explanation:
# 
# 
# The element at index 0 must be prime. Increment nums[0] = 1 to 2, using 1
# operation.
# The element at index 1 must be non-prime. Increment nums[1] = 2 to 4, using 2
# operations.
# The element at index 2 is already prime.
# The element at index 3 is already non-prime.
# 
# 
# Total operations = 1 + 2 = 3.
# 
# 
# Example 2:
# 
# 
# Input: nums = [5,6,7,8]
# 
# Output: 0
# 
# Explanation:
# 
# 
# The elements at indices 0 and 2 are already prime.
# The elements at indices 1 and 3 are already non-prime.
# 
# 
# No operations are needed.
# 
# 
# Example 3:
# 
# 
# Input: nums = [4,4]
# 
# Output: 1
# 
# Explanation:
# 
# 
# The element at index 0 must be prime. Increment nums[0] = 4 to 5, using 1
# operation.
# The element at index 1 is already non-prime.
# 
# 
# Total operations = 1.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 10^5
# 1 <= nums[i] <= 10^5
# 
# 
#

# @lc code=start
class Solution:
    def minOperations(self, nums: list[int]) -> int:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We are given an array `nums`.  We may increment any element by `1`, as
        many times as needed.  The final array must satisfy:

        * index 0, 2, 4, ...: the value is prime
        * index 1, 3, 5, ...: the value is non-prime

        We need the minimum total number of increments.

        Important observation: every position is independent
        ----------------------------------------------------
        Incrementing `nums[i]` does not change any other element, and there is
        no requirement such as "all values must be distinct" or "the array must
        be sorted".  Therefore the global optimum is simply the sum of the best
        local choice for each index.

        For each index:

        * Even index:
          We need the smallest prime number `p >= nums[i]`.  The contribution is
          `p - nums[i]`.

        * Odd index:
          We need the smallest non-prime number `x >= nums[i]`.
          If `nums[i]` is already non-prime, the cost is `0`.
          If `nums[i]` is prime, the next non-prime is extremely close:

              - if nums[i] == 2, then 3 is prime, so the next non-prime is 4;
                cost = 2
              - if nums[i] is an odd prime greater than 2, then nums[i] + 1 is
                an even number greater than 2, so it is non-prime; cost = 1

        Why use a sieve?
        ----------------
        We may have up to 100,000 numbers, and each value may be as large as
        100,000.  Checking primality by trial division for every value and every
        "next prime" search would repeat a lot of work.

        A Sieve of Eratosthenes precomputes primality for all relevant numbers
        once.  Then:

        * `is_prime[x]` answers "is x prime?" in O(1)
        * `next_prime[x]` answers "what is the smallest prime >= x?" in O(1)

        How far does the sieve need to go?
        ----------------------------------
        Even indices may need a prime slightly larger than max(nums).  The
        constraints have max(nums) <= 100,000.  Using `2 * max_value + 10` is a
        comfortable bound here: for every integer n > 1, Bertrand's postulate
        guarantees at least one prime between n and 2n.  For tiny values we also
        keep the limit at least 10.

        Algorithm
        ---------
        1. Let `limit = max(10, 2 * max(nums) + 10)`.
        2. Build `is_prime` with the Sieve of Eratosthenes up to `limit`.
        3. Build `next_prime` by scanning from right to left:
              last = -1
              for x from limit down to 0:
                  if is_prime[x]: last = x
                  next_prime[x] = last
        4. Scan the array:
              - even index: add `next_prime[value] - value`
              - odd index:
                    if value is non-prime, add 0
                    if value == 2, add 2
                    otherwise value is an odd prime, add 1

        Correctness proof
        -----------------
        We prove that the algorithm returns the minimum number of operations.

        Lemma 1: The optimal operation count for one index is independent of all
        other indices.
        An operation increments exactly one element, and the final validity of
        index `i` only depends on the final value at index `i` and on the parity
        of `i`.  No condition connects two different indices.  Therefore choices
        made for different indices cannot help or hurt each other.

        Lemma 2: For an even index with value `v`, the minimum cost is
        `next_prime[v] - v`.
        The final value must be prime and cannot be below `v`, because operations
        only increment.  Any valid final value is therefore a prime `p >= v`.
        The smallest such prime gives the fewest increments, exactly
        `next_prime[v] - v`.

        Lemma 3: For an odd index with value `v`, the algorithm adds the minimum
        cost needed to make the value non-prime.
        If `v` is already non-prime, zero operations are clearly optimal.  If
        `v == 2`, then `3` is also prime, and `4` is non-prime, so the minimum
        cost is 2.  If `v` is a prime greater than 2, then `v` is odd, making
        `v + 1` an even number greater than 2, hence non-prime; since `v` itself
        is not allowed, cost 1 is optimal.

        Theorem: The algorithm returns the global minimum operation count.
        By Lemma 1, the global optimum is the sum of the independent per-index
        optima.  By Lemma 2 the algorithm computes the optimum for every even
        index, and by Lemma 3 it computes the optimum for every odd index.
        Therefore the total returned by the algorithm is globally optimal.

        Complexity analysis
        -------------------
        Let:
            n = len(nums)
            M = max(nums)
            L = O(M), the sieve limit

        Sieve construction costs O(L log log L), the standard complexity of the
        Sieve of Eratosthenes.  Building the `next_prime` table costs O(L).
        Scanning the input costs O(n).

        Total time:  O(L log log L + n), which is O(M log log M + n)
        Total space: O(L), for `is_prime` and `next_prime`

        Why this is better than trial division
        --------------------------------------
        Trial division would check divisibility up to sqrt(x), and searching for
        the next prime could check several candidates.  That is still sometimes
        fine for small input, but with 100,000 array elements the repeated work
        is unnecessary.  The sieve pays a one-time preprocessing cost and makes
        all later prime queries constant-time.

        Edge cases to mention in an interview
        -------------------------------------
        * `1` is non-prime, so at an odd index it costs 0; at an even index it
          becomes 2 with cost 1.
        * `2` at an odd index is the only prime that needs cost 2, because
          `2 -> 3` is still prime.
        * Values already satisfying their index rule add 0.
        * A single-element array only needs the even-index prime rule.
        * Large values near 100,000 are handled because the sieve is extended
          beyond the maximum input value.

        Test strategy
        -------------
        Useful tests:

        * Examples:
              [1, 2, 3, 4] -> 3
              [5, 6, 7, 8] -> 0
              [4, 4]       -> 1

        * Small edge cases:
              [1] -> 1, because index 0 must become prime: 1 -> 2
              [2, 2] -> 2, because index 1 must become non-prime: 2 -> 4
              [1, 1] -> 1, because only index 0 must change

        * Already valid arrays:
              [2, 1, 3, 4] -> 0

        * Mixed arrays:
              even indices that need the next prime,
              odd indices that are prime and need one or two increments.
        """

        max_value = max(nums)
        limit = max(10, 2 * max_value + 10)

        is_prime = [True] * (limit + 1)
        is_prime[0] = False
        is_prime[1] = False

        p = 2
        while p * p <= limit:
            if is_prime[p]:
                for multiple in range(p * p, limit + 1, p):
                    is_prime[multiple] = False
            p += 1

        next_prime = [-1] * (limit + 1)
        closest = -1
        for value in range(limit, -1, -1):
            if is_prime[value]:
                closest = value
            next_prime[value] = closest

        operations = 0
        for index, value in enumerate(nums):
            if index % 2 == 0:
                operations += next_prime[value] - value
            elif is_prime[value]:
                operations += 2 if value == 2 else 1

        return operations
# @lc code=end
