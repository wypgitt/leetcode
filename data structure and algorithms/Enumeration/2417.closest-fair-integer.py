#
# @lc app=leetcode id=2417 lang=python3
#
# [2417] Closest Fair Integer
#
# https://leetcode.com/problems/closest-fair-integer/description/
#
# algorithms
# Medium (43.62%)
# Likes:    29
# Dislikes: 13
# Total Accepted:    1.5K
# Total Submissions: 3.4K
# Testcase Example:  "2"
#
#
# You are given a positive integer n.
#
# We call an integer k fair if the number of even digits in k is equal to
# the number of odd digits in it.
#
# Return the smallest fair integer that is greater than or equal to n.
#
# Example 1:
#
# Input: n = 2
# Output: 10
# Explanation: The smallest fair integer that is greater than or equal to
# 2 is 10.
# 10 is fair because it has an equal number of even and odd digits (one
# odd digit and one even digit).
#
# Example 2:
#
# Input: n = 403
# Output: 1001
# Explanation: The smallest fair integer that is greater than or equal to
# 403 is 1001.
# 1001 is fair because it has an equal number of even and odd digits (two
# odd digits and two even digits).
#
# Constraints:
#
# 1 <= n <= 10^9
#
# @lc code=start
class Solution:
    def closestFair(self, n: int) -> int:
        """
        Interview explanation:
        Premium. A fair number has equally many even and odd digits. Return the
        smallest fair integer >= n.

        Algorithm:
        - If digit count odd, jump to smallest even-length with half even/odd
          (10^d). Else scan upward from n (digit count small) / construct next
          fair candidate by adjusting digits.

        Complexity: O(poly(digits)) practical; digits <= 10 for constraints.
        """
        def is_fair(x: int) -> bool:
            even = odd = 0
            if x == 0:
                return False
            while x:
                if (x % 10) % 2 == 0:
                    even += 1
                else:
                    odd += 1
                x //= 10
            return even == odd and even > 0

        s = str(n)
        if len(s) % 2 == 1:
            # next even length: 10^len(s) has 1 and then zeros -> not fair;
            # smallest fair with 2k digits: k odds and k evens, minimal is
            # 10...(with proper parity). Known jump: 10**len(s) then search, but
            # 10^d itself may need bump. Brute from 10^len is fine (small).
            n = 10 ** len(s)

        # Constraints: n <= 10^9 typically in premium; still safe to scan with
        # structured search for larger. Use incremental check.
        while not is_fair(n):
            n += 1
            # If we rolled into odd digit length, jump again
            if len(str(n)) % 2 == 1:
                n = 10 ** len(str(n))
        return n
# @lc code=end
