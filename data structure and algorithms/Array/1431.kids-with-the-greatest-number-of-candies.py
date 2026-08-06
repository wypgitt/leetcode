#
# @lc app=leetcode id=1431 lang=python3
#
# [1431] Kids With the Greatest Number of Candies
#
# https://leetcode.com/problems/kids-with-the-greatest-number-of-candies/description/
#
# algorithms
# Easy (88.01%)
# Likes:    5022
# Dislikes: 637
# Total Accepted:    1.6M
# Total Submissions: 1.8M
# Testcase Example:  "[2,3,5,1,3]"
#
# There are n kids with candies. You are given an integer array candies, where
# each candies[i] represents the number of candies the i^th kid has, and an
# integer extraCandies, denoting the number of extra candies that you have.
#
# Return a boolean array result of length n, where result[i] is true if, after
# giving the i^th kid all the extraCandies, they will have the greatest number
# of candies among all the kids, or false otherwise.
#
# Note that multiple kids can have the greatest number of candies.
#
# Example 1:
#
# Input: candies = [2,3,5,1,3], extraCandies = 3
# Output: [true,true,true,false,true]
# Explanation: If you give all extraCandies to:
# - Kid 1, they will have 2 + 3 = 5 candies, which is the greatest among the
# kids.
# - Kid 2, they will have 3 + 3 = 6 candies, which is the greatest among the
# kids.
# - Kid 3, they will have 5 + 3 = 8 candies, which is the greatest among the
# kids.
# - Kid 4, they will have 1 + 3 = 4 candies, which is not the greatest among
# the kids.
# - Kid 5, they will have 3 + 3 = 6 candies, which is the greatest among the
# kids.
#
# Example 2:
#
# Input: candies = [4,2,1,1,2], extraCandies = 1
# Output: [true,false,false,false,false]
# Explanation: There is only 1 extra candy.
# Kid 1 will always have the greatest number of candies, even if a different
# kid is given the extra candy.
#
# Example 3:
#
# Input: candies = [12,1,12], extraCandies = 10
# Output: [true,false,true]
#
# Constraints:
#
# n == candies.length
#
# 2 <= n <= 100
#
# 1 <= candies[i] <= 100
#
# 1 <= extraCandies <= 50
#

# @lc code=start
from typing import List


class Solution:
    def kidsWithCandies(self, candies: List[int], extraCandies: int) -> List[bool]:
        """
        Interview explanation:
        After giving a kid all extraCandies, can they reach the current global
        max? Compare candies[i]+extra >= max(candies).

        Algorithm:
        - m=max(candies); return [c+extra>=m for c in candies]

        Complexity: O(n) time, O(1) extra (output excluded).
        """
        m = max(candies)
        return [c + extraCandies >= m for c in candies]

    def kidsWithCandies_scan(self, candies: List[int], extraCandies: int) -> List[bool]:
        """
        Interview explanation:
        Alternate explicit loop building the boolean list.

        Algorithm:
        - Same max then append flags.

        Complexity: O(n) time, O(n) space for answer.
        """
        m = 0
        for c in candies:
            if c > m:
                m = c
        ans = []
        for c in candies:
            ans.append(c + extraCandies >= m)
        return ans
# @lc code=end
