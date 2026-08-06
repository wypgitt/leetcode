#
# @lc app=leetcode id=553 lang=python3
#
# [553] Optimal Division
#
# https://leetcode.com/problems/optimal-division/description/
#
# algorithms
# Medium (62.98%)
# Likes:    422
# Dislikes: 1638
# Total Accepted:    52.3K
# Total Submissions: 83.1K
# Testcase Example:  '[1000,100,10,2]'
#
# You are given an integer array nums. The adjacent integers in nums will
# perform the float division.
# 
# 
# For example, for nums = [2,3,4], we will evaluate the expression "2/3/4".
# 
# 
# However, you can add any number of parenthesis at any position to change the
# priority of operations. You want to add these parentheses such the value of
# the expression after the evaluation is maximum.
# 
# Return the corresponding expression that has the maximum value in string
# format.
# 
# Note: your expression should not contain redundant parenthesis.
# 
# 
# Example 1:
# 
# 
# Input: nums = [1000,100,10,2]
# Output: "1000/(100/10/2)"
# Explanation: 1000/(100/10/2) = 1000/((100/10)/2) = 200
# However, the bold parenthesis in "1000/((100/10)/2)" are redundant since they
# do not influence the operation priority.
# So you should return "1000/(100/10/2)".
# Other cases:
# 1000/(100/10)/2 = 50
# 1000/(100/(10/2)) = 50
# 1000/100/10/2 = 0.5
# 1000/100/(10/2) = 2
# 
# 
# Example 2:
# 
# 
# Input: nums = [2,3,4]
# Output: "2/(3/4)"
# Explanation: (2/(3/4)) = 8/3 = 2.667
# It can be shown that after trying all possibilities, we cannot get an
# expression with evaluation greater than 2.667
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 10
# 2 <= nums[i] <= 1000
# There is only one optimal division for the given input.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def optimalDivision(self, nums: List[int]) -> str:
        if len(nums) == 1:
            return str(nums[0])
        if len(nums) == 2:
            return f"{nums[0]}/{nums[1]}"
        return f"{nums[0]}/(" + '/'.join(map(str, nums[1:])) + ')'
# @lc code=end

"""
Interview explanation:
To maximize nums[0] / nums[1] / nums[2] / ..., make the denominator as small as possible. Placing all remaining divisions inside one denominator gives nums[0] / (nums[1] / nums[2] / ...), which is maximal because every nums[i] for i>=2 moves to the numerator of the overall value.

Data structure: string construction only.

Edge cases: one number has no division; two numbers need no parentheses because parentheses would not change the value.

Complexity: O(n) time and O(n) space for the output string.
"""
