#
# @lc app=leetcode id=2802 lang=python3
#
# [2802] Find The K-th Lucky Number
#
# https://leetcode.com/problems/find-the-k-th-lucky-number/description/
#
# algorithms
# Medium (75.76%)
# Likes:    64
# Dislikes: 15
# Total Accepted:    6.4K
# Total Submissions: 8.4K
# Testcase Example:  "4"
#
#
# We know that 4 and 7 are lucky digits. Also, a number is called lucky if
# it contains only lucky digits.
#
# You are given an integer k, return the k^th lucky number represented as
# a string.
#
# Example 1:
#
# Input: k = 4
# Output: "47"
# Explanation: The first lucky number is 4, the second one is 7, the third
# one is 44 and the fourth one is 47.
#
# Example 2:
#
# Input: k = 10
# Output: "477"
# Explanation: Here are lucky numbers sorted in increasing order:
# 4, 7, 44, 47, 74, 77, 444, 447, 474, 477. So the 10^th lucky number is
# 477.
#
# Example 3:
#
# Input: k = 1000
# Output: "777747447"
# Explanation: It can be shown that the 1000^th lucky number is 777747447.
#
# Constraints:
#
# 1 <= k <= 10^9
#
# @lc code=start
class Solution:
    def kthLuckyNumber(self, k: int) -> str:
        """
        Interview explanation:
        Premium: a lucky number uses only digits 4 and 7. Return the k-th
        lucky number in ascending order as a string (1-indexed).
        Sequence: 4, 7, 44, 47, 74, 77, ...

        Algorithm:
        - Lucky numbers of length L are binary strings mapped 0->4, 1->7.
        - Equivalent: bin(k+1) without the leading '1' bit, map 0->4, 1->7.

        Complexity: O(log k) time, O(log k) space.
        """
        return bin(k + 1)[3:].replace("0", "4").replace("1", "7")

    def kthLuckyNumber_length_walk(self, k: int) -> str:
        """
        Interview explanation:
        Alternate: find length then pick bits by subtracting 2^(remaining).

        Algorithm:
        - While k > 2^n, subtract 2^n and increase length n.
        - For each position, choose 4 if k fits in left half else 7.

        Complexity: O(log k) time, O(log k) space.
        """
        n = 1
        while k > (1 << n):
            k -= 1 << n
            n += 1
        ans = []
        while n:
            n -= 1
            if k <= (1 << n):
                ans.append("4")
            else:
                ans.append("7")
                k -= 1 << n
        return "".join(ans)
# @lc code=end
