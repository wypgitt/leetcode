#
# @lc app=leetcode id=3790 lang=python3
#
# [3790] Smallest All-Ones Multiple
#
# https://leetcode.com/problems/smallest-all-ones-multiple/description/
#
# algorithms
# Medium (47.06%)
# Likes:    97
# Dislikes: 7
# Total Accepted:    28.3K
# Total Submissions: 60.1K
# Testcase Example:  "3"
#
#
# You are given a positive integer k.
#
# Find the smallest integer n divisible by k that consists of only the
# digit 1 in its decimal representation (e.g., 1, 11, 111, ...).
#
# Return an integer denoting the number of digits in the decimal
# representation of n. If no such n exists, return -1.
#
# Example 1:
#
# Input: k = 3
#
# Output: 3
#
# Explanation:
#
# n = 111 because 111 is divisible by 3, but 1 and 11 are not. The length
# of n = 111 is 3.
#
# Example 2:
#
# Input: k = 7
#
# Output: 6
#
# Explanation:
#
# n = 111111. The length of n = 111111 is 6.
#
# Example 3:
#
# Input: k = 2
#
# Output: -1
#
# Explanation:
#
# There does not exist a valid n that is a multiple of 2.
#
# Constraints:
#
# 2 <= k <= 10^5
#

# @lc code=start
class Solution:
    def minAllOneMultiple(self, k: int) -> int:
        """
        Interview explanation:
        Find the shortest repunit R(n)=111...1 (n ones) divisible by k. If k shares
        a factor with 10 (i.e. divisible by 2 or 5), no such repunit exists.

        Algorithm:
        - Early reject when k % 2 == 0 or k % 5 == 0.
        - Maintain rem = R(n) % k via rem = (rem*10+1) % k for n = 1..k.
        - First n with rem == 0 is the answer; else -1 (pigeonhole).

        Complexity: O(k) time, O(1) space.
        """
        if k % 2 == 0 or k % 5 == 0:
            return -1
        rem = 0
        for n in range(1, k + 1):
            rem = (rem * 10 + 1) % k
            if rem == 0:
                return n
        return -1

    def minAllOneMultiple_seen(self, k: int) -> int:
        """
        Interview explanation:
        Alternate: same modular growth, stop early if a remainder repeats (cycle).

        Algorithm:
        - Grow rem; track seen remainders; return length on rem==0, else -1 on cycle.

        Complexity: O(k) time, O(k) space.
        """
        if k % 2 == 0 or k % 5 == 0:
            return -1
        rem = 0
        seen = set()
        n = 0
        while rem not in seen:
            seen.add(rem)
            rem = (rem * 10 + 1) % k
            n += 1
            if rem == 0:
                return n
        return -1
# @lc code=end
