#
# @lc app=leetcode id=3927 lang=python3
#
# [3927] Minimize Array Sum Using Divisible Replacements
#
# https://leetcode.com/problems/minimize-array-sum-using-divisible-replacements/description/
#
# algorithms
# Medium (32.26%)
# Likes:    75
# Dislikes: 2
# Total Accepted:    23.4K
# Total Submissions: 72.6K
# Testcase Example:  "[3,6,2]"
#
#
# You are given an integer array nums.
#
# You can perform the following operation any number of times:
#
# Choose two indices a and b such that nums[a] % nums[b] == 0.
#
# Replace nums[a] with nums[b].
#
# Return the minimum possible sum of the array after performing any number
# of operations.
#
# Example 1:
#
# Input: nums = [3,6,2]
#
# Output: 7
#
# Explanation:
#
# Choose a = 1, b = 2, where nums[a] = 6 and nums[b] = 2. Since 6 % 2 ==
# 0, replace nums[1] with nums[2].
#
# The array becomes [3, 2, 2].
#
# No further operation reduces the sum. Thus, the final sum is 3 + 2 + 2 =
# 7.
#
# Example 2:
#
# Input: nums = [4,2,8,3]
#
# Output: 9
#
# Explanation:
#
# Choose a = 0, b = 1, where nums[a] = 4 and nums[b] = 2. Since 4 % 2 ==
# 0, replace nums[0] with nums[1].
#
# Choose a = 2, b = 1, where nums[a] = 8 and nums[b] = 2. Since 8 % 2 ==
# 0, replace nums[2] with nums[1].
#
# The array becomes [2, 2, 2, 3].
#
# No further operation reduces the sum. Thus, the final sum is 2 + 2 + 2 +
# 3 = 9.
#
# Example 3:
#
# Input: nums = [7,5,9]
#
# Output: 21
#
# Explanation:
#
# There is no pair (a, b) such that nums[a] % nums[b] == 0.
#
# Hence, no operation can be performed. The sum remains 7 + 5 + 9 = 21.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^​​​​​​​5
#

# @lc code=start

class Solution:
    def minArraySum(self, nums: list[int]) -> int:
        """
        Interview explanation:
        Replacing a multiple with a divisor that appears in the array can chain;
        each value can become the smallest array value that divides it.

        Algorithm:
        - Collect unique values; for each v, mark multiples and keep the minimum
          divisor present in the set (harmonic sweep up to max(nums)).
        - Sum the minimum divisor for every original element.

        Complexity: O(U + M log M) time (M = max value), O(U) space.
        """
        s = set(nums)
        max_n = max(s)
        min_div = {v: v for v in s}
        for v in sorted(s):
            for mult in range(v * 2, max_n + 1, v):
                if mult in min_div:
                    if v < min_div[mult]:
                        min_div[mult] = v
        return sum(min_div[x] for x in nums)
# @lc code=end
