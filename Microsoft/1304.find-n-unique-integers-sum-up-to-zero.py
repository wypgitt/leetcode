#
# @lc app=leetcode id=1304 lang=python3
#
# [1304] Find N Unique Integers Sum up to Zero
#
# https://leetcode.com/problems/find-n-unique-integers-sum-up-to-zero/description/
#
# algorithms
# Easy (78.43%)
# Likes:    2506
# Dislikes: 622
# Total Accepted:    406K
# Total Submissions: 518K
# Testcase Example:  "5"
#
# Given an integer n, return any array containing n unique integers such that
# they add up to 0.
#
# Example 1:
#
# Input: n = 5
# Output: [-7,-1,1,3,4]
# Explanation: These arrays also are accepted [-5,-1,1,2,3] , [-3,-1,2,-2,4].
#
# Example 2:
#
# Input: n = 3
# Output: [-1,0,1]
#
# Example 3:
#
# Input: n = 1
# Output: [0]
#
# Constraints:
#
# 1 <= n <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def sumZero(self, n: int) -> List[int]:
        """
        Interview explanation:
        Construct n distinct integers summing to 0: pairs (+i,-i), plus 0 if n odd.

        Algorithm:
        - For i=1..n//2 append i,-i; if n odd append 0.

        Complexity: O(n) time/space.
        """
        ans = []
        for i in range(1, n // 2 + 1):
            ans.extend([i, -i])
        if n % 2:
            ans.append(0)
        return ans
# @lc code=end

