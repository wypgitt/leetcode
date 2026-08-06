#
# @lc app=leetcode id=1689 lang=python3
#
# [1689] Partitioning Into Minimum Number Of Deci-Binary Numbers
#
# https://leetcode.com/problems/partitioning-into-minimum-number-of-deci-binary-numbers/description/
#
# algorithms
# Medium (90.47%)
# Likes:    2843
# Dislikes: 1547
# Total Accepted:    383K
# Total Submissions: 423K
# Testcase Example:  "\"32\""
#
# A decimal number is called deci-binary if each of its digits is either 0 or 1
# without any leading zeros. For example, 101 and 1100 are deci-binary, while
# 112 and 3001 are not.
#
# Given a string n that represents a positive decimal integer, return the
# minimum number of positive deci-binary numbers needed so that they sum up to
# n.
#
# Example 1:
#
# Input: n = "32"
# Output: 3
# Explanation: 10 + 11 + 11 = 32
#
# Example 2:
#
# Input: n = "82734"
# Output: 8
#
# Example 3:
#
# Input: n = "27346209830709182346"
# Output: 9
#
# Constraints:
#
# 1 <= n.length <= 10^5
#
# n consists of only digits.
#
# n does not contain any leading zeros and represents a positive integer.
#

# @lc code=start
class Solution:
    def minPartitions(self, n: str) -> int:
        """
        Interview explanation:
        Deci-binary digits are 0/1 only; any number is sum of deci-binary numbers
        equal to its max digit (place-wise).

        Algorithm:
        - return max digit in n

        Complexity: O(len(n)) time, O(1) space.
        """
        return int(max(n))
# @lc code=end
