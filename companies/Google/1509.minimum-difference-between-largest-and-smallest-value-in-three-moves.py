#
# @lc app=leetcode id=1509 lang=python3
#
# [1509] Minimum Difference Between Largest and Smallest Value in Three Moves
#
# https://leetcode.com/problems/minimum-difference-between-largest-and-smallest-value-in-three-moves/description/
#
# algorithms
# Medium (59.2%)
# Likes:    2559
# Dislikes: 287
# Total Accepted:    253K
# Total Submissions: 427K
# Testcase Example:  "[5,3,2,4]"
#
# You are given an integer array nums.
#
# In one move, you can choose one element of nums and change it to any value.
#
# Return the minimum difference between the largest and smallest value of nums
# after performing at most three moves.
#
# Example 1:
#
# Input: nums = [5,3,2,4]
# Output: 0
# Explanation: We can make at most 3 moves.
# In the first move, change 2 to 3. nums becomes [5,3,3,4].
# In the second move, change 4 to 3. nums becomes [5,3,3,3].
# In the third move, change 5 to 3. nums becomes [3,3,3,3].
# After performing 3 moves, the difference between the minimum and maximum is 3
# - 3 = 0.
#
# Example 2:
#
# Input: nums = [1,5,0,10,14]
# Output: 1
# Explanation: We can make at most 3 moves.
# In the first move, change 5 to 0. nums becomes [1,0,0,10,14].
# In the second move, change 10 to 0. nums becomes [1,0,0,0,14].
# In the third move, change 14 to 1. nums becomes [1,0,0,0,1].
# After performing 3 moves, the difference between the minimum and maximum is 1
# - 0 = 1.
# It can be shown that there is no way to make the difference 0 in 3 moves.
#
# Example 3:
#
# Input: nums = [3,100,20]
# Output: 0
# Explanation: We can make at most 3 moves.
# In the first move, change 100 to 7. nums becomes [3,7,20].
# In the second move, change 20 to 7. nums becomes [3,7,7].
# In the third move, change 3 to 7. nums becomes [7,7,7].
# After performing 3 moves, the difference between the minimum and maximum is 7
# - 7 = 0.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^9 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def minDifference(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Change at most 3 elements to minimize max-min of the array. Sort; the
        optimal is to "discard" 3 extremes from the ends — try the 4 cases:
        change 3 largest, 2 largest+1 smallest, 1 largest+2 smallest, 3 smallest.

        Algorithm:
        - If n<=4 return 0; sort; min(nums[n-4+i]-nums[i] for i in 0..3).

        Complexity: O(n log n) time, O(1) extra.
        """
        n = len(nums)
        if n <= 4:
            return 0
        nums.sort()
        return min(nums[n - 4 + i] - nums[i] for i in range(4))
# @lc code=end
