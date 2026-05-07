#
# @lc app=leetcode id=3881 lang=python3
#
# [3881] Direction Assignments with Exactly K Visible People
#
# https://leetcode.com/problems/direction-assignments-with-exactly-k-visible-people/description/
#
# algorithms
# Medium (36.30%)
# Likes:    60
# Dislikes: 18
# Total Accepted:    15.3K
# Total Submissions: 42.2K
# Testcase Example:  '3\n1\n0'
#
# You are given three integers n, pos, and k.
# 
# There are n people standing in a line indexed from 0 to n - 1. Each person
# independently chooses a direction:
# 
# 
# 'L': visible only to people on their right
# 'R': visible only to people on their left
# 
# A person at index pos sees others as follows:
# 
# 
# A person i < pos is visible if and only if they choose 'L'.
# A person i > pos is visible if and only if they choose 'R'.
# 
# 
# Return the number of possible direction assignments such that the person at
# index pos sees exactly k people.
# 
# Since the answer may be large, return it modulo 10^9 + 7.
# 
# 
# Example 1:
# 
# 
# Input: n = 3, pos = 1, k = 0
# 
# Output: 2
# 
# Explanation:​​​​​​​
# 
# 
# Index 0 is to the left of pos = 1, and index 2 is to the right of pos =
# 1.
# To see k = 0 people, index 0 must choose 'R' and index 2 must choose 'L',
# keeping both invisible.
# The person at index 1 can choose 'L' or 'R' since it does not affect the
# count. Thus, the answer is 2.
# 
# 
# 
# Example 2:
# 
# 
# Input: n = 3, pos = 2, k = 1
# 
# Output: 4
# 
# Explanation:
# 
# 
# Index 0 and index 1 are left of pos = 2, and there is no index to the
# right.
# To see k = 1 person, exactly one of index 0 or index 1 must choose 'L', and
# the other must choose 'R'.
# There are 2 ways to choose which index is visible from the left.
# The person at index 2 can choose 'L' or 'R' since it does not affect the
# count. Thus, the answer is 2 + 2 = 4.
# 
# 
# 
# Example 3:
# 
# 
# Input: n = 1, pos = 0, k = 0
# 
# Output: 2
# 
# Explanation:
# 
# 
# There are no indices to the left or right of pos = 0.
# To see k = 0 people, no additional condition is required.
# The person at index 0 can choose 'L' or 'R'. Thus, the answer is 2.
# 
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 10^5
# 0 <= pos, k <= n - 1
# 
# 
#

# @lc code=start
class Solution:
    def countVisiblePeople(self, n: int, pos: int, k: int) -> int:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        There are `n` people in a line.  Each person chooses one direction:

            'L' or 'R'

        We focus only on the person at index `pos`.

        Visibility rule:

        * If another person is left of `pos`, meaning `i < pos`, then that
          person is visible to `pos` exactly when they choose 'L'.
        * If another person is right of `pos`, meaning `i > pos`, then that
          person is visible to `pos` exactly when they choose 'R'.
        * The direction chosen by the person at `pos` does not affect how many
          other people are visible.

        We need the number of direction assignments where exactly `k` people are
        visible to `pos`, modulo 1,000,000,007.

        Key observation
        ---------------
        Every person except `pos` has exactly:

        * one direction that makes them visible
        * one direction that makes them invisible

        For example:

        * left side person:
              visible direction = 'L'
              invisible direction = 'R'

        * right side person:
              visible direction = 'R'
              invisible direction = 'L'

        So after we decide WHICH `k` of the `n - 1` other people are visible,
        all their directions are forced:

        * selected visible people use their visible direction
        * all other people use their invisible direction

        The person at `pos` can independently choose either 'L' or 'R', giving
        a factor of 2.

        Formula
        -------
        There are `n - 1` people other than `pos`.

        Choose exactly `k` of them to be visible:

            C(n - 1, k)

        Then multiply by 2 for the direction of the person at `pos`:

            answer = 2 * C(n - 1, k)

        Notice that `pos` does not appear in the final formula.  Its only role is
        deciding which direction is the visible direction for each side, but each
        non-pos person still contributes exactly one visible choice and one
        invisible choice.

        Data structure / math choice
        ----------------------------
        We need compute one binomial coefficient modulo:

            MOD = 1,000,000,007

        This modulus is prime.  We can compute:

            C(total, k) = total! / (k! * (total - k)!)

        under the modulus using modular inverses:

            inverse(x) = pow(x, MOD - 2, MOD)

        by Fermat's little theorem.

        Since `n <= 100000`, precomputing factorials and inverse factorials up
        to `n - 1` is easy and reliable.

        Algorithm
        ---------
        1. Let `total = n - 1`, the number of people other than `pos`.
        2. If `k > total`, return 0.  Under the given constraints this will not
           happen because `k <= n - 1`, but the guard makes the function robust.
        3. Precompute:

               factorial[i] = i! mod MOD

           for `0 <= i <= total`.

        4. Precompute inverse factorials:

               inv_factorial[total] = inverse(factorial[total])
               inv_factorial[i - 1] = inv_factorial[i] * i

        5. Compute:

               combinations =
                   factorial[total]
                   * inv_factorial[k]
                   * inv_factorial[total - k]

        6. Return:

               2 * combinations mod MOD

        Correctness proof
        -----------------
        Lemma 1: For every person `i != pos`, choosing whether they are visible
        uniquely determines their direction.
        If `i < pos`, they are visible exactly with direction 'L' and invisible
        exactly with direction 'R'.  If `i > pos`, they are visible exactly with
        direction 'R' and invisible exactly with direction 'L'.  In either case,
        each visibility choice maps to exactly one direction.

        Lemma 2: For every subset of exactly `k` people among the `n - 1` people
        other than `pos`, there is exactly one assignment of directions for
        those `n - 1` people that makes precisely that subset visible.
        By Lemma 1, each selected person must take their unique visible
        direction, and each unselected person must take their unique invisible
        direction.  This assignment is forced and valid.

        Lemma 3: The person at `pos` contributes exactly 2 independent choices.
        The problem's visibility count only depends on other people's directions.
        The direction chosen by the person at `pos` does not change who is
        visible.  Therefore `pos` can choose either 'L' or 'R' for every valid
        assignment of the other people.

        Theorem: The algorithm returns the number of valid assignments.
        There are exactly `C(n - 1, k)` choices for the visible subset of other
        people.  By Lemma 2, each subset corresponds to exactly one assignment
        for the other people.  By Lemma 3, each such assignment extends to
        exactly 2 full assignments including `pos`.  Therefore the total is
        `2 * C(n - 1, k)`, which is exactly what the algorithm computes.

        Complexity analysis
        -------------------
        Let `N = n - 1`.

        Precomputing factorials and inverse factorials up to `N` costs O(N).
        The final combination calculation is O(1).

        Total time:  O(n)
        Total space: O(n)

        Can we do less space?
        ---------------------
        Yes.  Since we only need one binomial coefficient, we could compute:

            C(N, k) = product_{i=1..k} (N - k + i) / i

        using modular inverses and only O(1) extra space.  That would take
        O(min(k, N - k) log MOD) time if each inverse is computed separately.

        For `n <= 100000`, factorial precomputation is simple, fast, and the
        standard interview/contest approach for modular combinations.

        Edge cases
        ----------
        * n = 1, k = 0:
          There are no other people.  The only choices are the direction of
          `pos`, so answer = 2.

        * k = 0:
          Nobody else is visible.  Every other person's direction is forced to
          invisible, and `pos` has 2 choices.

        * k = n - 1:
          Everybody else is visible.  Every other person's direction is forced
          to visible, and `pos` has 2 choices.

        * pos at either end:
          All other people are on one side, but each still has exactly one
          visible direction and one invisible direction, so the same formula
          applies.

        Test strategy
        -------------
        Useful tests:

        * Provided examples:
              n = 3, pos = 1, k = 0 -> 2
              n = 3, pos = 2, k = 1 -> 4
              n = 1, pos = 0, k = 0 -> 2

        * Extremes:
              k = 0
              k = n - 1
              pos = 0
              pos = n - 1

        * Small n brute force:
          Enumerate all 2^n direction assignments and count visible people to
          confirm the formula.
        """

        mod = 1_000_000_007
        total = n - 1

        if k > total:
            return 0

        factorial = [1] * (total + 1)
        for value in range(1, total + 1):
            factorial[value] = factorial[value - 1] * value % mod

        inverse_factorial = [1] * (total + 1)
        inverse_factorial[total] = pow(factorial[total], mod - 2, mod)
        for value in range(total, 0, -1):
            inverse_factorial[value - 1] = inverse_factorial[value] * value % mod

        combinations = factorial[total]
        combinations = combinations * inverse_factorial[k] % mod
        combinations = combinations * inverse_factorial[total - k] % mod

        return 2 * combinations % mod
# @lc code=end
