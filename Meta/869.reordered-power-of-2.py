#
# @lc app=leetcode id=869 lang=python3
#
# [869] Reordered Power of 2
#
# https://leetcode.com/problems/reordered-power-of-2/description/
#
# algorithms
# Medium (65.86%)
# Likes:    2547
# Dislikes: 499
# Total Accepted:    232K
# Total Submissions: 352K
# Testcase Example:  "1"
#
# You are given an integer n. We reorder the digits in any order (including the
# original order) such that the leading digit is not zero.
#
# Return true if and only if we can do this so that the resulting number is a
# power of two.
#
# Example 1:
#
# Input: n = 1
# Output: true
#
# Example 2:
#
# Input: n = 10
# Output: false
#
# Constraints:
#
# 1 <= n <= 10^9
#

# @lc code=start
from collections import Counter


class Solution:
    def reorderedPowerOf2(self, n: int) -> bool:
        """
        Interview explanation:
        n's digits can rearrange to a power of 2 iff some 2^k has the same
        digit multiset. Check signatures of all 2^k in int range.

        Algorithm:
        - sig = sorted digit string (or Counter).
        - For k=0..30, compare sig(2^k) with sig(n).

        Complexity: O(log n * D log D) with D<=10 digits; tiny constant.
        """
        target = "".join(sorted(str(n)))
        for k in range(31):
            if "".join(sorted(str(1 << k))) == target:
                return True
        return False

    def reorderedPowerOf2_counter(self, n: int) -> bool:
        """
        Interview explanation:
        Alternate: Counter digit frequency comparison vs powers of two.

        Algorithm:
        - cnt = Counter(str(n)); check Counter(str(1<<k)) == cnt.

        Complexity: O(1) for fixed digit length bound.
        """
        cnt = Counter(str(n))
        return any(Counter(str(1 << k)) == cnt for k in range(31))
# @lc code=end

