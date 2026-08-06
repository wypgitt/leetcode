#
# @lc app=leetcode id=1399 lang=python3
#
# [1399] Count Largest Group
#
# https://leetcode.com/problems/count-largest-group/description/
#
# algorithms
# Easy (74.66%)
# Likes:    813
# Dislikes: 1193
# Total Accepted:    190K
# Total Submissions: 254K
# Testcase Example:  "13"
#
# You are given an integer n.
#
# We need to group the numbers from 1 to n according to the sum of its digits.
# For example, the numbers 14 and 5 belong to the same group, whereas 13 and 3
# belong to different groups.
#
# Return the number of groups that have the largest size, i.e. the maximum
# number of elements.
#
# Example 1:
#
# Input: n = 13
# Output: 4
# Explanation: There are 9 groups in total, they are grouped according sum of
# its digits of numbers from 1 to 13:
# [1,10], [2,11], [3,12], [4,13], [5], [6], [7], [8], [9].
# There are 4 groups with largest size.
#
# Example 2:
#
# Input: n = 2
# Output: 2
# Explanation: There are 2 groups [1], [2] of size 1.
#
# Constraints:
#
# 1 <= n <= 10^4
#

# @lc code=start

from collections import Counter


class Solution:
    def countLargestGroup(self, n: int) -> int:
        """
        Interview explanation:
        Group integers 1..n by digit-sum; return how many groups share the
        maximum size.

        Algorithm:
        - Counter of digit sums; count values equal to max frequency

        Complexity: O(n log n) digit work, O(1) groups (max sum 9*digits).
        """
        def digit_sum(x: int) -> int:
            s = 0
            while x:
                s += x % 10
                x //= 10
            return s

        cnt = Counter(digit_sum(i) for i in range(1, n + 1))
        mx = max(cnt.values())
        return sum(1 for v in cnt.values() if v == mx)
# @lc code=end
