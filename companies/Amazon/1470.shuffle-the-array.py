#
# @lc app=leetcode id=1470 lang=python3
#
# [1470] Shuffle the Array
#
# https://leetcode.com/problems/shuffle-the-array/description/
#
# algorithms
# Easy (88.7%)
# Likes:    6508
# Dislikes: 361
# Total Accepted:    1.2M
# Total Submissions: 1.3M
# Testcase Example:  "[2,5,1,3,4,7]"
#
# Given the array nums consisting of 2n elements in the form
# [x_1,x_2,...,x_n,y_1,y_2,...,y_n].
#
# Return the array in the form [x_1,y_1,x_2,y_2,...,x_n,y_n].
#
# Example 1:
#
# Input: nums = [2,5,1,3,4,7], n = 3
# Output: [2,3,5,4,1,7]
# Explanation: Since x_1=2, x_2=5, x_3=1, y_1=3, y_2=4, y_3=7 then the answer
# is [2,3,5,4,1,7].
#
# Example 2:
#
# Input: nums = [1,2,3,4,4,3,2,1], n = 4
# Output: [1,4,2,3,3,2,4,1]
#
# Example 3:
#
# Input: nums = [1,1,2,2], n = 2
# Output: [1,2,1,2]
#
# Constraints:
#
# 1 <= n <= 500
#
# nums.length == 2n
#
# 1 <= nums[i] <= 10^3
#

# @lc code=start
from typing import List


class Solution:
    def shuffle(self, nums: List[int], n: int) -> List[int]:
        """
        Interview explanation:
        Given [x1..xn,y1..yn], return [x1,y1,...,xn,yn].

        Algorithm:
        - Build result by zipping first and second halves.

        Complexity: O(n) time, O(n) space.
        """
        return [v for pair in zip(nums[:n], nums[n:]) for v in pair]

    def shuffle_index(self, nums: List[int], n: int) -> List[int]:
        """
        Interview explanation:
        Alternate: explicit index loop appending nums[i], nums[i+n].

        Algorithm:
        - For i in 0..n-1 append nums[i], nums[i+n].

        Complexity: O(n) time, O(n) space.
        """
        ans = []
        for i in range(n):
            ans.append(nums[i])
            ans.append(nums[i + n])
        return ans
# @lc code=end
