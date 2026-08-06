#
# @lc app=leetcode id=3766 lang=python3
#
# [3766] Minimum Operations to Make Binary Palindrome
#
# https://leetcode.com/problems/minimum-operations-to-make-binary-palindrome/description/
#
# algorithms
# Medium (52.28%)
# Likes:    56
# Dislikes: 10
# Total Accepted:    18.2K
# Total Submissions: 34.8K
# Testcase Example:  "[1,2,4]"
#
#
# You are given an integer array nums.
#
# For each element nums[i], you may perform the following operations any
# number of times (including zero):
#
# Increase nums[i] by 1, or
#
# Decrease nums[i] by 1.
#
# A number is called a binary palindrome if its binary representation
# without leading zeros reads the same forward and backward.
#
# Your task is to return an integer array ans, where ans[i] represents the
# minimum number of operations required to convert nums[i] into a binary
# palindrome.
#
# Example 1:
#
# Input: nums = [1,2,4]
#
# Output: [0,1,1]
#
# Explanation:
#
# One optimal set of operations:
#
#                         nums[i]
#                         Binary(nums[i])
#                         Nearest
#
#                         Palindrome
#                         Binary
#
#                         (Palindrome)
#                         Operations Required
#                         ans[i]
#
#                         1
#                         1
#                         1
#                         1
#                         Already palindrome
#                         0
#
#                         2
#                         10
#                         3
#                         11
#                         Increase by 1
#                         1
#
#                         4
#                         100
#                         3
#                         11
#                         Decrease by 1
#                         1
#
# Thus, ans = [0, 1, 1].
#
# Example 2:
#
# Input: nums = [6,7,12]
#
# Output: [1,0,3]
#
# Explanation:
#
# One optimal set of operations:
#
#                         nums[i]
#                         Binary(nums[i])
#                         Nearest
#
#                         Palindrome
#                         Binary
#
#                         (Palindrome)
#                         Operations Required
#                         ans[i]
#
#                         6
#                         110
#                         5
#                         101
#                         Decrease by 1
#                         1
#
#                         7
#                         111
#                         7
#                         111
#                         Already palindrome
#                         0
#
#                         12
#                         1100
#                         15
#                         1111
#                         Increase by 3
#                         3
#
# Thus, ans = [1, 0, 3].
#
# Constraints:
#
# 1 <= nums.length <= 5000
#
# ^​​​​​​​1 <= nums[i] <=^ 5000
#

# @lc code=start
from typing import List
import bisect


def _binary_palindromes(limit: int) -> List[int]:
    pals = []
    for x in range(1, limit + 1):
        b = bin(x)[2:]
        if b == b[::-1]:
            pals.append(x)
    # allow going slightly above max nums via larger pals for nearest-above
    for x in range(limit + 1, (1 << 14)):
        b = bin(x)[2:]
        if b == b[::-1]:
            pals.append(x)
            if x > limit + 100:  # enough headroom for nearest above 5000
                break
    return pals


_PALS = _binary_palindromes(5000)


class Solution:
    def minOperations(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        nums[i] <= 5000, so precompute all binary palindromes and map each value
        to the nearest one by absolute difference.

        Algorithm:
        - Generate binary palindromes; for each x bisect to neighbors; take min |diff|.

        Complexity: O(P + n log P) preprocess/query, O(P) space.
        """
        ans = []
        for x in nums:
            i = bisect.bisect_left(_PALS, x)
            best = 10**9
            if i < len(_PALS):
                best = min(best, _PALS[i] - x)
            if i > 0:
                best = min(best, x - _PALS[i - 1])
            ans.append(best)
        return ans

    def minOperations_scan(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate: for each x walk outward until a binary palindrome is found.

        Algorithm:
        - is_pal via bin string; expand delta = 0,1,2,... until hit.

        Complexity: O(n * D) for distance D to nearest pal, O(1) extra space.
        """
        def is_pal(x: int) -> bool:
            if x <= 0:
                return False
            b = bin(x)[2:]
            return b == b[::-1]

        ans = []
        for x in nums:
            d = 0
            while True:
                if is_pal(x + d) or (x - d > 0 and is_pal(x - d)):
                    ans.append(d)
                    break
                d += 1
        return ans
# @lc code=end
