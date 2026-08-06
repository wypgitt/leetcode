#
# @lc app=leetcode id=3556 lang=python3
#
# [3556] Sum of Largest Prime Substrings
#
# https://leetcode.com/problems/sum-of-largest-prime-substrings/description/
#
# algorithms
# Medium (38.22%)
# Likes:    60
# Dislikes: 11
# Total Accepted:    25.7K
# Total Submissions: 67.2K
# Testcase Example:  "\"12234\""
#
#
# Given a string s, find the sum of the 3 largest unique prime numbers
# that can be formed using any of its substrings.
#
# Return the sum of the three largest unique prime numbers that can be
# formed. If fewer than three exist, return the sum of all available
# primes. If no prime numbers can be formed, return 0.
#
# Note: Each prime number should be counted only once, even if it appears
# in multiple substrings. Additionally, when converting a substring to an
# integer, any leading zeros are ignored.
#
# Example 1:
#
# Input: s = "12234"
#
# Output: 1469
#
# Explanation:
#
# The unique prime numbers formed from the substrings of "12234" are 2, 3,
# 23, 223, and 1223.
#
# The 3 largest primes are 1223, 223, and 23. Their sum is 1469.
#
# Example 2:
#
# Input: s = "111"
#
# Output: 11
#
# Explanation:
#
# The unique prime number formed from the substrings of "111" is 11.
#
# Since there is only one prime number, the sum is 11.
#
# Constraints:
#
# 1 <= s.length <= 10
#
# s consists of only digits.
#

# @lc code=start
class Solution:
    def sumOfLargestPrimes(self, s: str) -> int:
        """
        Interview explanation:
        All substring integers (leading zeros ignored by int()) that are prime;
        sum the up to 3 largest unique values. Length ≤ 10 ⇒ enumerate all O(n^2)
        substrings.

        Algorithm:
        - Collect unique int(s[i:j]) that are prime.
        - Sort descending and sum the top 3 (or fewer).

        Complexity: O(n^2 * √A) time for primality, O(n^2) space.
        """
        def is_prime(x: int) -> bool:
            if x < 2:
                return False
            if x % 2 == 0:
                return x == 2
            d = 3
            while d * d <= x:
                if x % d == 0:
                    return False
                d += 2
            return True

        primes = set()
        n = len(s)
        for i in range(n):
            for j in range(i + 1, n + 1):
                val = int(s[i:j])
                if is_prime(val):
                    primes.add(val)
        top = sorted(primes, reverse=True)[:3]
        return sum(top)
# @lc code=end
