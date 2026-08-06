#
# @lc app=leetcode id=740 lang=python3
#
# [740] Delete and Earn
#
# https://leetcode.com/problems/delete-and-earn/description/
#
# algorithms
# Medium (57.45%)
# Likes:    8049
# Dislikes: 407
# Total Accepted:    465K
# Total Submissions: 810K
# Testcase Example:  "[3,4,2]"
#
# You are given an integer array nums. You want to maximize the number of
# points you get by performing the following operation any number of times:
#
# Pick any nums[i] and delete it to earn nums[i] points. Afterwards, you must
# delete every element equal to nums[i] - 1 and every element equal to nums[i]
# + 1.
#
# Return the maximum number of points you can earn by applying the above
# operation some number of times.
#
# Example 1:
#
# Input: nums = [3,4,2]
# Output: 6
# Explanation: You can perform the following operations:
# - Delete 4 to earn 4 points. Consequently, 3 is also deleted. nums = [2].
# - Delete 2 to earn 2 points. nums = [].
# You earn a total of 6 points.
#
# Example 2:
#
# Input: nums = [2,2,3,3,3,4]
# Output: 9
# Explanation: You can perform the following operations:
# - Delete a 3 to earn 3 points. All 2's and 4's are also deleted. nums =
# [3,3].
# - Delete a 3 again to earn 3 points. nums = [3].
# - Delete a 3 once more to earn 3 points. nums = [].
# You earn a total of 9 points.
#
# Constraints:
#
# 1 <= nums.length <= 2 * 10^4
#
# 1 <= nums[i] <= 10^4
#


# @lc code=start
from typing import List


class Solution:
    def deleteAndEarn(self, nums: List[int]) -> int:
        """
        Interview explanation:
        House-robber reduction: points[v] = v * count(v). Taking v forbids v-1
        and v+1, so on the value line we either take points[v] + skip previous,
        or skip v — same recurrence as House Robber.

        Algorithm:
        - Build points[0..max]; take = skip = 0
        - For v in 0..max: take, skip = skip + points[v], max(skip, take)

        Complexity: O(n + M) time where M = max(nums); O(M) space.
        """
        if not nums:
            return 0
        m = max(nums)
        points = [0] * (m + 1)
        for x in nums:
            points[x] += x
        take = skip = 0
        for v in range(m + 1):
            take, skip = skip + points[v], max(skip, take)
        return max(take, skip)
# @lc code=end

