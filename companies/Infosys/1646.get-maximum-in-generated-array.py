#
# @lc app=leetcode id=1646 lang=python3
#
# [1646] Get Maximum in Generated Array
#
# https://leetcode.com/problems/get-maximum-in-generated-array/description/
#
# algorithms
# Easy (51.61%)
# Likes:    790
# Dislikes: 968
# Total Accepted:    127K
# Total Submissions: 247K
# Testcase Example:  "7"
#
# You are given an integer n. A 0-indexed integer array nums of length n + 1 is
# generated in the following way:
#
# nums[0] = 0
#
# nums[1] = 1
#
# nums[2 * i] = nums[i] when 2 <= 2 * i <= n
#
# nums[2 * i + 1] = nums[i] + nums[i + 1] when 2 <= 2 * i + 1 <= n
#
# Return the maximum integer in the array nums.
#
# Example 1:
#
# Input: n = 7
# Output: 3
# Explanation: According to the given rules:
# nums[0] = 0
# nums[1] = 1
# nums[(1 * 2) = 2] = nums[1] = 1
# nums[(1 * 2) + 1 = 3] = nums[1] + nums[2] = 1 + 1 = 2
# nums[(2 * 2) = 4] = nums[2] = 1
# nums[(2 * 2) + 1 = 5] = nums[2] + nums[3] = 1 + 2 = 3
# nums[(3 * 2) = 6] = nums[3] = 2
# nums[(3 * 2) + 1 = 7] = nums[3] + nums[4] = 2 + 1 = 3
# Hence, nums = [0,1,1,2,1,3,2,3], and the maximum is max(0,1,1,2,1,3,2,3) = 3.
#
# Example 2:
#
# Input: n = 2
# Output: 1
# Explanation: According to the given rules, nums = [0,1,1]. The maximum is
# max(0,1,1) = 1.
#
# Example 3:
#
# Input: n = 3
# Output: 2
# Explanation: According to the given rules, nums = [0,1,1,2]. The maximum is
# max(0,1,1,2) = 2.
#
# Constraints:
#
# 0 <= n <= 100
#

# @lc code=start
class Solution:
    def getMaximumGenerated(self, n: int) -> int:
        """
        Interview explanation:
        Generate nums where nums[2i]=nums[i], nums[2i+1]=nums[i]+nums[i+1];
        return max in nums[0..n].

        Algorithm (simulation):
        - Build array size n+1; fill by rules; return max.

        Complexity: O(n) time/space.
        """
        if n == 0:
            return 0
        nums = [0] * (n + 1)
        nums[1] = 1
        for i in range(2, n + 1):
            if i % 2 == 0:
                nums[i] = nums[i // 2]
            else:
                nums[i] = nums[i // 2] + nums[i // 2 + 1]
        return max(nums)

    def getMaximumGenerated_inplace(self, n: int) -> int:
        """
        Interview explanation:
        Alternate fill using even/odd index formula in one loop.

        Algorithm:
        - Same generation; track running maximum.

        Complexity: O(n) time/space.
        """
        if n == 0:
            return 0
        nums = [0] * (n + 1)
        nums[1] = 1
        ans = 1
        for i in range(1, n // 2 + 1):
            if 2 * i <= n:
                nums[2 * i] = nums[i]
                ans = max(ans, nums[2 * i])
            if 2 * i + 1 <= n:
                nums[2 * i + 1] = nums[i] + nums[i + 1]
                ans = max(ans, nums[2 * i + 1])
        return ans
# @lc code=end
