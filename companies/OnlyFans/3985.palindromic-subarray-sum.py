#
# @lc app=leetcode id=3985 lang=python3
#
# [3985] Palindromic Subarray Sum
#
# https://leetcode.com/problems/palindromic-subarray-sum/description/
#
# algorithms
# Hard (34.32%)
# Likes:    42
# Dislikes: 6
# Total Accepted:    6.2K
# Total Submissions: 17.9K
# Testcase Example:  "[10,10]"
#
#
# You are given an integer array nums.
#
# Return the maximum possible sum of a subarray of nums that is a
# palindrome.
#
# Example 1:
#
# Input: nums = [10,10]
#
# Output: 20
#
# Explanation:
#
# The whole array [10,10] is a palindrome. Therefore, the maximum sum is
# 10 + 10 = 20.
#
# Example 2:
#
# Input: nums = [1,2,3,2,1,5,6]
#
# Output: 9
#
# Explanation:
#
# The contiguous subarray [1,2,3,2,1] is a palindrome. Its sum is 1 + 2 +
# 3 + 2 + 1 = 9 and it is the maximum sum.
#
# Example 3:
#
# Input: nums = [7,1,2,1,7,3,4,3,4]
#
# Output: 18
#
# Explanation:
#
# The contiguous subarray [7,1,2,1,7] is a palindrome. Its sum is 7 + 1 +
# 2 + 1 + 7 = 18 and it is the maximum sum.
#
# Example 4:
#
# Input: nums = [1,2,3,4,5]
#
# Output: 5
#
# Explanation:
#
# No subarray with length greater than 1 is a palindrome. The largest
# element in the array is 5. Therefore, the answer is 5.
#
# Example 5:
#
# Input: nums = [1000]
#
# Output: 1000
#
# Explanation:
#
# The subarray with only one element is a palindrome. Therefore, the
# answer is 1000.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^​​​​​​​9
#

# @lc code=start
from typing import List


class Solution:
    def getSum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Values are positive, so around each center the longest palindromic
        subarray has the maximum sum. Compute all longest palindromes with
        Manacher; evaluate sums via prefix sums.

        Algorithm:
        - Build prefix sums for O(1) range sums.
        - Manacher odd radii d1 and even radii d2; take each longest
          palindrome's sum and keep the max (at least max element).

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        pref = [0] * (n + 1)
        for i, x in enumerate(nums):
            pref[i + 1] = pref[i] + x

        def rng(l: int, r: int) -> int:
            return pref[r + 1] - pref[l]

        ans = max(nums)

        d1 = [0] * n
        l = r = -1
        for i in range(n):
            k = 1 if i > r else min(d1[l + r - i], r - i + 1)
            while i - k >= 0 and i + k < n and nums[i - k] == nums[i + k]:
                k += 1
            d1[i] = k
            if i + k - 1 > r:
                l, r = i - k + 1, i + k - 1
            left, right = i - (d1[i] - 1), i + (d1[i] - 1)
            ans = max(ans, rng(left, right))

        d2 = [0] * n
        l = r = -1
        for i in range(n):
            k = 0 if i > r else min(d2[l + r - i + 1], r - i + 1)
            while i - k - 1 >= 0 and i + k < n and nums[i - k - 1] == nums[i + k]:
                k += 1
            d2[i] = k
            if i + k - 1 > r:
                l, r = i - k, i + k - 1
            if d2[i]:
                left, right = i - d2[i], i + d2[i] - 1
                ans = max(ans, rng(left, right))
        return ans
# @lc code=end
