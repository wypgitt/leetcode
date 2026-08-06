#
# @lc app=leetcode id=483 lang=python3
#
# [483] Smallest Good Base
#
# https://leetcode.com/problems/smallest-good-base/description/
#
# algorithms
# Hard (46.02%)
# Likes:    427
# Dislikes: 540
# Total Accepted:    31.8K
# Total Submissions: 69.1K
# Testcase Example:  '"13"'
#
# Given an integer n represented as a string, return the smallest good base of
# n.
# 
# We call k >= 2 a good base of n, if all digits of n base k are 1's.
# 
# 
# Example 1:
# 
# 
# Input: n = "13"
# Output: "3"
# Explanation: 13 base 3 is 111.
# 
# 
# Example 2:
# 
# 
# Input: n = "4681"
# Output: "8"
# Explanation: 4681 base 8 is 11111.
# 
# 
# Example 3:
# 
# 
# Input: n = "1000000000000000000"
# Output: "999999999999999999"
# Explanation: 1000000000000000000 base 999999999999999999 is 11.
# 
# 
# 
# Constraints:
# 
# 
# n is an integer in the range [3, 10^18].
# n does not contain any leading zeros.
# 
# 
#

# @lc code=start
class Solution:
    def smallestGoodBase(self, n: str) -> str:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We are given an integer `n` as a string.  We need find the smallest base
        `k >= 2` such that the representation of `n` in base `k` contains only
        digit `1`.

        Examples:

            13 in base 3 is 111:
                13 = 1 * 3^2 + 1 * 3^1 + 1

            4681 in base 8 is 11111:
                4681 = 8^4 + 8^3 + 8^2 + 8 + 1

        Convert the condition into math
        -------------------------------
        If `n` is written as `m + 1` ones in base `k`, then:

            n = 1 + k + k^2 + ... + k^m

        where:

            k >= 2
            m >= 1

        The case `m = 1` means:

            n = 1 + k
            k = n - 1

        So every `n >= 3` always has at least one good base: `n - 1`, because
        `n` is `"11"` in base `n - 1`.

        Goal
        ----
        We need the smallest base `k`, not the shortest representation.

        For a fixed `n`, using more digits of `1` requires a smaller base.  For
        example, if:

            n = 1 + k + k^2 + ... + k^m

        then larger `m` generally forces smaller `k`.

        Therefore, to find the smallest base, we try the largest possible `m`
        first.  The first valid base we find is the answer.

        Maximum possible length
        -----------------------
        The smallest allowed base is 2.  So the longest possible all-ones
        representation happens in base 2.

        If there are `m + 1` ones:

            n >= 1 + 2 + 2^2 + ... + 2^m
              = 2^(m + 1) - 1

        Since `n <= 10^18`, `m` is at most about 60.  This is tiny.

        Searching for a base for a fixed m
        ----------------------------------
        For fixed `m`, define:

            f(k) = 1 + k + k^2 + ... + k^m

        This function is strictly increasing for `k >= 2`.  So we can binary
        search for a base `k` such that:

            f(k) == n

        If `f(k) < n`, the base is too small.
        If `f(k) > n`, the base is too large.

        Avoiding overflow / huge intermediate work
        ------------------------------------------
        Python integers do not overflow, but computing huge powers unnecessarily
        is still wasteful.  The helper `geometric_sum` builds:

            1 + base + base^2 + ... + base^m

        iteratively and stops early if the sum already exceeds `n`.

        This keeps each check fast.

        Algorithm
        ---------
        1. Convert `n` to integer `number`.
        2. Let `max_power = number.bit_length() - 1`.  This is a safe upper
           bound for `m`.
        3. For `power` from `max_power` down to 2:
              - binary search `base` from 2 to `number - 1`
              - compute `1 + base + ... + base^power`
              - if it equals `number`, return `base`
        4. If no longer representation works, return `number - 1`, which always
           gives representation `"11"`.

        Why loop down to 2 and not 1?
        ----------------------------
        `power = 1` is the guaranteed fallback:

            n = 1 + (n - 1)

        We only need to search for representations with at least 3 ones
        (`power >= 2`) because any such representation would produce a smaller
        base than `n - 1`.

        Data structure choice
        ---------------------
        No complex data structure is needed.  This is a number-theory problem
        solved with:

        * integer binary search
        * a geometric-sum helper

        Correctness proof
        -----------------
        Lemma 1: A base `k` is good for `n` if and only if there exists an
        integer `m >= 1` such that
        `n = 1 + k + k^2 + ... + k^m`.
        This is exactly the value of a base-`k` number whose digits are all `1`.

        Lemma 2: For fixed `m`, the function
        `f(k) = 1 + k + k^2 + ... + k^m` is strictly increasing for `k >= 2`.
        If `k` increases, every positive power term `k^i` for `i >= 1`
        increases, so the whole sum increases.

        Lemma 3: For a fixed `m`, binary search finds a good base with that `m`
        if one exists.
        By Lemma 2, `f(k)` is monotonic.  Binary search over possible bases
        therefore correctly determines whether some integer base has
        `f(k) == n`.

        Lemma 4: The smallest good base corresponds to the largest possible
        exponent `m`.
        If `n = 1 + k + ... + k^m`, then for larger `m`, the same `n` must be
        represented with a smaller base because the sum contains more positive
        terms.  Thus among valid representations, the one with largest `m`
        gives the smallest base.

        Lemma 5: The fallback `number - 1` is always a valid good base.
        In base `number - 1`, the number is:

            number = 1 * (number - 1) + 1

        so its representation is `"11"`.

        Theorem: The algorithm returns the smallest good base.
        By Lemma 3, for each exponent it correctly detects whether a valid base
        exists.  The algorithm checks exponents from largest to smallest, so by
        Lemma 4 the first valid base found is the smallest possible.  If none is
        found for `m >= 2`, Lemma 5 gives the only needed fallback for `m = 1`.

        Complexity analysis
        -------------------
        Let:

            N = int(n)
            L = floor(log2 N), at most about 60

        We try O(L) possible exponents.  For each exponent, binary search over
        the base range costs O(log N) iterations.  Each geometric-sum check
        multiplies/adds up to O(L) terms, stopping early when possible.

        Total time:

            O((log N)^3)

        With `N <= 10^18`, this is very small in practice.

        Extra space:

            O(1)

        Edge cases
        ----------
        * n = "3":
          Answer is "2", because 3 is "11" in base 2.

        * n has no representation with 3 or more ones:
          Return n - 1.

        * Very large n:
          We never convert to floating point, so there are no precision issues.

        * Perfect geometric sums:
          Binary search detects exact equality.

        Test strategy
        -------------
        Useful tests:

        * Provided examples:
              "13"                  -> "3"
              "4681"                -> "8"
              "1000000000000000000" -> "999999999999999999"

        * Small values:
              "3" -> "2"
              "7" -> "2"
              "15" -> "2"

        * Numbers where the fallback is required:
              "10" -> "9"

        Possible improvement?
        ---------------------
        Some solutions estimate the base with floating-point roots for each
        exponent, then verify.  That can be faster, but it risks precision bugs
        near `10^18`.  The all-integer binary search is slightly more work but
        very robust and still easily fast enough.
        """

        number = int(n)

        def geometric_sum(base: int, power: int, limit: int) -> int:
            total = 1
            term = 1

            for _ in range(power):
                term *= base
                total += term
                if total > limit:
                    break

            return total

        max_power = number.bit_length() - 1

        for power in range(max_power, 1, -1):
            left = 2
            right = number - 1

            while left <= right:
                middle = (left + right) // 2
                current_sum = geometric_sum(middle, power, number)

                if current_sum == number:
                    return str(middle)

                if current_sum < number:
                    left = middle + 1
                else:
                    right = middle - 1

        return str(number - 1)
# @lc code=end
