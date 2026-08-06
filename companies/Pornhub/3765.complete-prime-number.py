#
# @lc app=leetcode id=3765 lang=python3
#
# [3765] Complete Prime Number
#
# https://leetcode.com/problems/complete-prime-number/description/
#
# algorithms
# Medium (36.52%)
# Likes:    53
# Dislikes: 4
# Total Accepted:    29.8K
# Total Submissions: 81.6K
# Testcase Example:  "23"
#
#
# You are given an integer num.
#
# A number num is called a Complete Prime Number if every prefix and every
# suffix of num is prime.
#
# Return true if num is a Complete Prime Number, otherwise return false.
#
# Note:
#
# A prefix of a number is formed by the first k digits of the number.
#
# A suffix of a number is formed by the last k digits of the number.
#
# Single-digit numbers are considered Complete Prime Numbers only if they
# are prime.
#
# Example 1:
#
# Input: num = 23
#
# Output: true
#
# Explanation:
#
# ​​​​​​​Prefixes of num = 23 are 2 and 23, both are prime.
#
# Suffixes of num = 23 are 3 and 23, both are prime.
#
# All prefixes and suffixes are prime, so 23 is a Complete Prime Number
# and the answer is true.
#
# Example 2:
#
# Input: num = 39
#
# Output: false
#
# Explanation:
#
# Prefixes of num = 39 are 3 and 39. 3 is prime, but 39 is not prime.
#
# Suffixes of num = 39 are 9 and 39. Both 9 and 39 are not prime.
#
# At least one prefix or suffix is not prime, so 39 is not a Complete
# Prime Number and the answer is false.
#
# Example 3:
#
# Input: num = 7
#
# Output: true
#
# Explanation:
#
# 7 is prime, so all its prefixes and suffixes are prime and the answer is
# true.
#
# Constraints:
#
# 1 <= num <= 10^9
#

# @lc code=start
class Solution:
    def completePrime(self, num: int) -> bool:
        """
        Interview explanation:
        Every prefix and every suffix (as integers) must be prime. Shrink the
        number from the left while building the suffix from the right.

        Algorithm:
        - is_prime via trial division.
        - While num > 0: require num and the reconstructed suffix both prime;
          peel the last digit into the suffix.

        Complexity: O(d * sqrt(num)) time for d digits, O(1) space.
        """
        def is_prime(n: int) -> bool:
            if n <= 1 or (n > 2 and n % 2 == 0):
                return False
            i = 3
            while i * i <= n:
                if n % i == 0:
                    return False
                i += 2
            return True

        suffix, base = 0, 1
        while num:
            if not is_prime(num):
                return False
            suffix += (num % 10) * base
            if not is_prime(suffix):
                return False
            num //= 10
            base *= 10
        return True

    def completePrime_string(self, num: int) -> bool:
        """
        Interview explanation:
        Alternate: check every prefix/suffix substring interpreted as int.

        Algorithm:
        - s = str(num); for k in 1..len(s) test int(s[:k]) and int(s[-k:]).

        Complexity: O(d * sqrt(num)) time, O(d) space.
        """
        def is_prime(n: int) -> bool:
            if n <= 1 or (n > 2 and n % 2 == 0):
                return False
            i = 3
            while i * i <= n:
                if n % i == 0:
                    return False
                i += 2
            return True

        s = str(num)
        for k in range(1, len(s) + 1):
            if not is_prime(int(s[:k])) or not is_prime(int(s[-k:])):
                return False
        return True
# @lc code=end
