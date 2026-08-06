#
# @lc app=leetcode id=3969 lang=python3
#
# [3969] Valid Subarrays With Matching Sum Digits I
#
# https://leetcode.com/problems/valid-subarrays-with-matching-sum-digits-i/description/
#
# algorithms
# Medium (46.65%)
# Likes:    49
# Dislikes: 4
# Total Accepted:    40K
# Total Submissions: 85.7K
# Testcase Example:  "[1,100,1]\n1"
#
#
# You are given an integer array nums and an integer digit x.
#
# A subarray nums[l..r] is considered valid if the sum of its elements
# satisfies both of the following conditions:
#
# The first digit of the sum is equal to x.
#
# The last digit of the sum is equal to x.
#
# Return the number of valid subarrays.
#
# Example 1:
#
# Input: nums = [1,100,1], x = 1
#
# Output: 4
#
# Explanation:
#
# The valid subarrays are:
#
# nums[0..0]: sum = 1
#
# nums[0..1]: sum = 1 + 100 = 101
#
# nums[1..2]: sum = 100 + 1 = 101
#
# nums[2..2]: sum = 1
#
# Thus, the answer is 4.
#
# Example 2:
#
# Input: nums = [1], x = 2
#
# Output: 0
#
# Explanation:
#
# The only subarray is nums[0..0] with a sum of 1, which does not satisfy
# the conditions.
#
# Thus, the answer is 0.
#
# Constraints:
#
# 1 <= nums.length <= 1500
#
# 1 <= nums[i] <= 10^9
#
# 1 <= x <= 9
#

# @lc code=start

class Solution:
    def countValidSubarrays(self, nums: list[int], x: int) -> int:
        """
        Interview explanation:
        With n <= 1500, enumerate all subarray sums and check first/last digits.

        Algorithm:
        - For each left index, extend right while maintaining the running sum.
        - Count sums whose last digit and first digit both equal x.

        Complexity: O(n^2) time, O(1) extra space.
        """
        n = len(nums)
        ans = 0
        for l in range(n):
            s = 0
            for r in range(l, n):
                s += nums[r]
                if s % 10 == x:
                    t = s
                    while t >= 10:
                        t //= 10
                    if t == x:
                        ans += 1
        return ans
# @lc code=end
