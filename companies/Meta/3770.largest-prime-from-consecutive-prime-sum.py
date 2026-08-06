#
# @lc app=leetcode id=3770 lang=python3
#
# [3770] Largest Prime from Consecutive Prime Sum
#
# https://leetcode.com/problems/largest-prime-from-consecutive-prime-sum/description/
#
# algorithms
# Medium (39.35%)
# Likes:    67
# Dislikes: 4
# Total Accepted:    26.1K
# Total Submissions: 66.3K
# Testcase Example:  "20"
#
#
# You are given an integer n.
#
# Return the largest prime number less than or equal to n that can be
# expressed as the sum of one or more consecutive prime numbers starting
# from 2. If no such number exists, return 0.
#
# Example 1:
#
# Input: n = 20
#
# Output: 17
#
# Explanation:
#
# The prime numbers less than or equal to n = 20 which are consecutive
# prime sums are:
#
# 2 = 2
#
# 5 = 2 + 3
#
# 17 = 2 + 3 + 5 + 7
#
# The largest is 17, so it is the answer.
#
# Example 2:
#
# Input: n = 2
#
# Output: 2
#
# Explanation:
#
# The only consecutive prime sum less than or equal to 2 is 2 itself.
#
# Constraints:
#
# 1 <= n <= 5 * 10^5
#

# @lc code=start
class Solution:
    def largestPrime(self, n: int) -> int:
        """
        Interview explanation:
        Among prefix sums of primes starting at 2, return the largest prime
        prefix sum that is <= n.

        Algorithm:
        - Sieve primes up to n; accumulate sums from 2; track when the sum itself is prime.

        Complexity: O(n log log n) time, O(n) space.
        """
        if n < 2:
            return 0
        is_prime = [True] * (n + 1)
        is_prime[0] = is_prime[1] = False
        primes = []
        for i in range(2, n + 1):
            if is_prime[i]:
                primes.append(i)
                step = i
                start = i * i
                for j in range(start, n + 1, step):
                    is_prime[j] = False
        total = 0
        ans = 0
        for p in primes:
            total += p
            if total > n:
                break
            if is_prime[total]:
                ans = total
        return ans

    def largestPrime_trial(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: generate primes by trial division while summing.

        Algorithm:
        - Walk candidates; if prime, add to sum; update answer when sum is prime and <= n.

        Complexity: O(n^{3/2}/log n) rough, O(pi(n)) space.
        """
        def is_prime(x: int) -> bool:
            if x <= 1 or (x > 2 and x % 2 == 0):
                return False
            i = 3
            while i * i <= x:
                if x % i == 0:
                    return False
                i += 2
            return True

        if n < 2:
            return 0
        total = 0
        ans = 0
        for x in range(2, n + 1):
            if not is_prime(x):
                continue
            total += x
            if total > n:
                break
            if is_prime(total):
                ans = total
        return ans
# @lc code=end
