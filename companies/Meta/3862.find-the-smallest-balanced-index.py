#
# @lc app=leetcode id=3862 lang=python3
#
# [3862] Find the Smallest Balanced Index
#
# https://leetcode.com/problems/find-the-smallest-balanced-index/description/
#
# algorithms
# Medium (19.52%)
# Likes:    100
# Dislikes: 19
# Total Accepted:    38.6K
# Total Submissions: 198K
# Testcase Example:  "[2,1,2]"
#
#
# You are given an integer array nums.
#
# An index i is balanced if the sum of elements strictly to the left of i
# equals the product of elements strictly to the right of i.
#
# If there are no elements to the left, the sum is considered as 0.
# Similarly, if there are no elements to the right, the product is
# considered as 1.
#
# Return an integer denoting the smallest balanced index. If no balanced
# index exists, return -1.
#
# Example 1:
#
# Input: nums = [2,1,2]
#
# Output: 1
#
# Explanation:
#
# For index i = 1:
#
# Left sum = nums[0] = 2
#
# Right product = nums[2] = 2
#
# Since the left sum equals the right product, index 1 is balanced.
#
# No smaller index satisfies the condition, so the answer is 1.
#
# Example 2:
#
# Input: nums = [2,8,2,2,5]
#
# Output: 2
#
# Explanation:
#
# For index i = 2:
#
# Left sum = 2 + 8 = 10
#
# Right product = 2 * 5 = 10
#
# Since the left sum equals the right product, index 2 is balanced.
#
# No smaller index satisfies the condition, so the answer is 2.
#
# Example 3:
#
# Input: nums = [1]
#
# Output: -1
#
# For index i = 0:
#
# The left side is empty, so the left sum is 0.
#
# The right side is empty, so the right product is 1.
#
# Since the left sum does not equal the right product, index 0 is not
# balanced.
#
# Therefore, no balanced index exists and the answer is -1.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
class Solution:
    def smallestBalancedIndex(self, nums: list[int]) -> int:
        """
        Interview explanation:
        Find smallest i with sum(left)==product(right). Positive nums ⇒ at most
        one such index (left sum ↑, right product ↓).

        Algorithm:
        - Scan i from right to left; s = left sum, p = right product.
        - On each i: s -= nums[i]; if s==p return i; then p *= nums[i].
        - Stop early once p >= s (further left cannot match).

        Complexity: O(n) time, O(1) space.
        """
        s = sum(nums)
        p = 1
        for i in range(len(nums) - 1, -1, -1):
            s -= nums[i]
            if s == p:
                return i
            p *= nums[i]
            if p >= s:
                break
        return -1
# @lc code=end
