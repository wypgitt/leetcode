#
# @lc app=leetcode id=1838 lang=python3
#
# [1838] Frequency of the Most Frequent Element
#
# https://leetcode.com/problems/frequency-of-the-most-frequent-element/description/
#
# algorithms
# Medium (45.09%)
# Likes:    5890
# Dislikes: 316
# Total Accepted:    293K
# Total Submissions: 649K
# Testcase Example:  "[1,2,4]"
#
# The frequency of an element is the number of times it occurs in an array.
#
# You are given an integer array nums and an integer k. In one operation, you
# can choose an index of nums and increment the element at that index by 1.
#
# Return the maximum possible frequency of an element after performing at most
# k operations.
#
# Example 1:
#
# Input: nums = [1,2,4], k = 5
# Output: 3
# Explanation: Increment the first element three times and the second element
# two times to make nums = [4,4,4].
# 4 has a frequency of 3.
#
# Example 2:
#
# Input: nums = [1,4,8,13], k = 5
# Output: 2
# Explanation: There are multiple optimal solutions:
# - Increment the first element three times to make nums = [4,4,8,13]. 4 has a
# frequency of 2.
# - Increment the second element four times to make nums = [1,8,8,13]. 8 has a
# frequency of 2.
# - Increment the third element five times to make nums = [1,4,13,13]. 13 has a
# frequency of 2.
#
# Example 3:
#
# Input: nums = [3,9,6], k = 2
# Output: 1
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#
# 1 <= k <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def maxFrequency(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Maximize frequency by incrementing others with budget k. After sort,
        make a window all equal to its right end; cost = x*len - sum.

        Algorithm (sort + sliding window):
        - Sort; expand r; shrink l while cost > k; track max length.

        Complexity: O(n log n) time, O(1)/O(n) space.
        """
        nums.sort()
        l = 0
        total = 0
        ans = 1
        for r, x in enumerate(nums):
            total += x
            while x * (r - l + 1) - total > k:
                total -= nums[l]
                l += 1
            ans = max(ans, r - l + 1)
        return ans

    def maxFrequency_binary_search(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Classic alternate: prefix sums + binary search longest window ending at r.

        Algorithm (prefix + binary search):
        - Sort; pref sums; for each r binary-search leftmost l with cost <= k.

        Complexity: O(n log n) time, O(n) space.
        """
        nums.sort()
        n = len(nums)
        pref = [0]
        for x in nums:
            pref.append(pref[-1] + x)
        ans = 1
        for r in range(n):
            lo, hi = 0, r
            best = r
            while lo <= hi:
                mid = (lo + hi) // 2
                need = nums[r] * (r - mid + 1) - (pref[r + 1] - pref[mid])
                if need <= k:
                    best = mid
                    hi = mid - 1
                else:
                    lo = mid + 1
            ans = max(ans, r - best + 1)
        return ans
# @lc code=end
