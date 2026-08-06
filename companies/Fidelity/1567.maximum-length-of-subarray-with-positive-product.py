#
# @lc app=leetcode id=1567 lang=python3
#
# [1567] Maximum Length of Subarray With Positive Product
#
# https://leetcode.com/problems/maximum-length-of-subarray-with-positive-product/description/
#
# algorithms
# Medium (44.76%)
# Likes:    2508
# Dislikes: 81
# Total Accepted:    114K
# Total Submissions: 254K
# Testcase Example:  "[1,-2,-3,4]"
#
# Given an array of integers nums, find the maximum length of a subarray where
# the product of all its elements is positive.
#
# A subarray of an array is a consecutive sequence of zero or more values taken
# out of that array.
#
# Return the maximum length of a subarray with positive product.
#
# Example 1:
#
# Input: nums = [1,-2,-3,4]
# Output: 4
# Explanation: The array nums already has a positive product of 24.
#
# Example 2:
#
# Input: nums = [0,1,-2,-3,-4]
# Output: 3
# Explanation: The longest subarray with positive product is [1,-2,-3] which
# has a product of 6.
# Notice that we cannot include 0 in the subarray since that'll make the
# product 0 which is not positive.
#
# Example 3:
#
# Input: nums = [-1,-2,-3,0,1]
# Output: 2
# Explanation: The longest subarray with positive product is [-1,-2] or
# [-2,-3].
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
    def getMaxLen(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Max length of subarray with positive product. Zeros reset. Track length
        of positive-product and negative-product suffixes; on negative swap.

        Algorithm (pos/neg lengths):
        - pos=neg=0; for x: if x==0 reset; elif x>0: pos+=1; neg=neg+1 if neg else 0;
          else: swap roles then extend. ans=max(ans,pos).

        Complexity: O(n) time, O(1) space.
        """
        ans = pos = neg = 0
        for x in nums:
            if x == 0:
                pos = neg = 0
            elif x > 0:
                pos += 1
                neg = neg + 1 if neg > 0 else 0
            else:
                new_pos = neg + 1 if neg > 0 else 0
                new_neg = pos + 1
                pos, neg = new_pos, new_neg
            ans = max(ans, pos)
        return ans

    def getMaxLen_segments(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: split by zeros; in each segment, if even #negatives whole
        length; else max of drop through first or last negative.

        Algorithm:
        - For each zero-free segment find first/last neg index and count.

        Complexity: O(n).
        """
        def solve(seg: List[int]) -> int:
            if not seg:
                return 0
            negs = [i for i, x in enumerate(seg) if x < 0]
            if len(negs) % 2 == 0:
                return len(seg)
            # drop prefix through first neg, or suffix through last neg
            return max(len(seg) - negs[0] - 1, negs[-1])

        ans = 0
        cur: List[int] = []
        for x in nums + [0]:
            if x == 0:
                ans = max(ans, solve(cur))
                cur = []
            else:
                cur.append(x)
        return ans
# @lc code=end

