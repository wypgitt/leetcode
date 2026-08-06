#
# @lc app=leetcode id=3171 lang=python3
#
# [3171] Find Subarray With Bitwise OR Closest to K
#
# https://leetcode.com/problems/find-subarray-with-bitwise-or-closest-to-k/description/
#
# algorithms
# Hard (31.49%)
# Likes:    217
# Dislikes: 8
# Total Accepted:    16.4K
# Total Submissions: 52.1K
# Testcase Example:  "[1,2,4,5]\n3"
#
#
# You are given an array nums and an integer k. You need to find a
# subarray of nums such that the absolute difference between k and the
# bitwise OR of the subarray elements is as small as possible. In other
# words, select a subarray nums[l..r] such that |k - (nums[l] OR nums[l +
# 1] ... OR nums[r])| is minimum.
#
# Return the minimum possible value of the absolute difference.
#
# A subarray is a contiguous non-empty sequence of elements within an
# array.
#
# Example 1:
#
# Input: nums = [1,2,4,5], k = 3
#
# Output: 0
#
# Explanation:
#
# The subarray nums[0..1] has OR value 3, which gives the minimum absolute
# difference |3 - 3| = 0.
#
# Example 2:
#
# Input: nums = [1,3,1,3], k = 2
#
# Output: 1
#
# Explanation:
#
# The subarray nums[1..1] has OR value 3, which gives the minimum absolute
# difference |3 - 2| = 1.
#
# Example 3:
#
# Input: nums = [1], k = 10
#
# Output: 9
#
# Explanation:
#
# There is a single subarray with OR value 1, which gives the minimum
# absolute difference |10 - 1| = 9.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# 1 <= k <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def minimumDifference(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Subarray OR is monotone non-decreasing as the left end moves left.
        Distinct OR values of subarrays ending at a fixed right index is O(bits).

        Algorithm:
        - Maintain the set of OR-results of subarrays ending at i-1.
        - Transition: new = {nums[i]} ∪ {prev | nums[i] for prev in old}.
        - Track min |or_val - k|.

        Complexity: O(n * B) time (B ~ 30), O(B) space.
        """
        ans = abs(nums[0] - k)
        cur: set[int] = set()
        for x in nums:
            nxt = {x}
            for v in cur:
                nxt.add(v | x)
            cur = nxt
            for v in cur:
                ans = min(ans, abs(v - k))
                if ans == 0:
                    return 0
        return ans

    def minimumDifference_list(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: keep a sorted unique list of ending-OR values; OR with x
        shrinks/merges the set (still O(bits)).

        Algorithm:
        - Same DP set idea with a list instead of a hash set.

        Complexity: O(n * B^2) time, O(B) space.
        """
        ans = abs(nums[0] - k)
        cur: list[int] = []
        for x in nums:
            nxt = [x]
            seen = {x}
            for v in cur:
                w = v | x
                if w not in seen:
                    seen.add(w)
                    nxt.append(w)
            cur = nxt
            for v in cur:
                ans = min(ans, abs(v - k))
        return ans
# @lc code=end
