#
# @lc app=leetcode id=3917 lang=python3
#
# [3917] Count Indices With Opposite Parity
#
# https://leetcode.com/problems/count-indices-with-opposite-parity/description/
#
# algorithms
# Easy (81.94%)
# Likes:    28
# Dislikes: 1
# Total Accepted:    42.9K
# Total Submissions: 52.3K
# Testcase Example:  "[1,2,3,4]"
#
#
# You are given an integer array nums of length n.
#
# The score of an index i is defined as the number of indices j such that:
#
# i < j < n, and
#
# nums[i] and nums[j] have different parity (one is even and the other is
# odd).
#
# Return an integer array answer of length n, where answer[i] is the score
# of index i.
#
# Example 1:
#
# Input: nums = [1,2,3,4]
#
# Output: [2,1,1,0]
#
# Explanation:
#
# nums[0] = 1, which is odd. Thus, the indices j = 1 and j = 3 satisfy the
# conditions, so the score of index 0 is 2.
#
# nums[1] = 2, which is even. Thus, the index j = 2 satisfies the
# conditions, so the score of index 1 is 1.
#
# nums[2] = 3, which is odd. Thus, the index j = 3 satisfies the
# conditions, so the score of index 2 is 1.
#
# nums[3] = 4, which is even. Thus, no index satisfies the conditions, so
# the score of index 3 is 0.
#
# Thus, the answer = [2, 1, 1, 0].
#
# Example 2:
#
# Input: nums = [1]
#
# Output: [0]
#
# Explanation:
#
# There is only one element in nums. Thus, the score of index 0 is 0.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 100
#

# @lc code=start
class Solution:
    def countOppositeParity(self, nums: list[int]) -> list[int]:
        """
        Interview explanation:
        answer[i] = count of later indices with opposite parity to nums[i].

        Algorithm:
        - Count total odd/even, then scan left→right subtracting the current
          element from the remaining opposite-parity count.

        Complexity: O(n) time, O(n) space for the answer.
        """
        odd = sum(x & 1 for x in nums)
        even = len(nums) - odd
        ans = []
        for x in nums:
            if x & 1:
                odd -= 1
                ans.append(even)
            else:
                even -= 1
                ans.append(odd)
        return ans
# @lc code=end
