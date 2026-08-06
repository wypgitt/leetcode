#
# @lc app=leetcode id=3759 lang=python3
#
# [3759] Count Elements With at Least K Greater Values
#
# https://leetcode.com/problems/count-elements-with-at-least-k-greater-values/description/
#
# algorithms
# Medium (31.92%)
# Likes:    78
# Dislikes: 7
# Total Accepted:    34K
# Total Submissions: 106.6K
# Testcase Example:  "[3,1,2]\n1"
#
#
# You are given an integer array nums of length n and an integer k.
#
# An element in nums is said to be qualified if there exist at least k
# elements in the array that are strictly greater than it.
#
# Return an integer denoting the total number of qualified elements in
# nums.
#
# Example 1:
#
# Input: nums = [3,1,2], k = 1
#
# Output: 2
#
# Explanation:
#
# The elements 1 and 2 each have at least k = 1 element greater than
# themselves.
#
# ​​​​​​​No element is greater than 3. Therefore, the answer is 2.
#
# Example 2:
#
# Input: nums = [5,5,5], k = 2
#
# Output: 0
#
# Explanation:
#
# Since all elements are equal to 5, no element is greater than the other.
# Therefore, the answer is 0.
#
# Constraints:
#
# 1 <= n == nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# 0 <= k < n
#

# @lc code=start
from typing import List


class Solution:
    def countElements(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        An element qualifies if at least k array values are strictly greater.

        Algorithm:
        - Sort ascending; for value at index i (0-based), there are n-1-i values
          to the right that are >= it — but equals are not greater, so use
          bisect: #greater(x) = n - upper_bound(x). Count those with #greater >= k.

        Complexity: O(n log n) time, O(n) space.
        """
        import bisect

        if k == 0:
            return len(nums)
        s = sorted(nums)
        n = len(s)
        ans = 0
        for x in nums:
            greater = n - bisect.bisect_right(s, x)
            if greater >= k:
                ans += 1
        return ans

    def countElements_freq(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: sort and sweep how many elements are strictly larger than each
        distinct value.

        Algorithm:
        - Sort; walk from the right accumulating counts of greater values.

        Complexity: O(n log n) time, O(n) space.
        """
        if k == 0:
            return len(nums)
        s = sorted(nums)
        n = len(s)
        # For each position in sorted order, #strictly greater is known after
        # skipping the equal run to the right.
        ans = 0
        i = 0
        while i < n:
            j = i
            while j < n and s[j] == s[i]:
                j += 1
            greater = n - j
            if greater >= k:
                ans += j - i
            i = j
        return ans
# @lc code=end
