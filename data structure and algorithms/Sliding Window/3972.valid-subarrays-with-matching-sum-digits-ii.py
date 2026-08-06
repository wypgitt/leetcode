#
# @lc app=leetcode id=3972 lang=python3
#
# [3972] Valid Subarrays With Matching Sum Digits II
#
# https://leetcode.com/problems/valid-subarrays-with-matching-sum-digits-ii/description/
#
# algorithms
# Hard (34.62%)
# Likes:    1
# Dislikes: 1
# Total Accepted:    234
# Total Submissions: 676
# Testcase Example:  "[1,100,1]\n1"
#
#
# You are given an integer array nums and an integer digit x.
#
# A subarray nums[l..r] is considered valid if the sum of its elements
# satisfies both of the following conditions:
#
# The first digit of the sum is equal to x.
#
# The last digit of the sum is equal to x.
#
# Return the number of valid subarrays.
#
# Example 1:
#
# Input: nums = [1,100,1], x = 1
#
# Output: 4
#
# Explanation:
#
# The valid subarrays are:
#
# nums[0..0]: sum = 1
#
# nums[0..1]: sum = 1 + 100 = 101
#
# nums[1..2]: sum = 100 + 1 = 101
#
# nums[2..2]: sum = 1
#
# Thus, the answer is 4.
#
# Example 2:
#
# Input: nums = [1], x = 2
#
# Output: 0
#
# Explanation:
#
# The only subarray is nums[0..0] with a sum of 1, which does not satisfy
# the conditions.
#
# Thus, the answer is 0.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# 1 <= x <= 9
#

# @lc code=start

from bisect import bisect_left, bisect_right


class Solution:
    def countValidSubarrays(self, nums: list[int], x: int) -> int:
        """
        Interview explanation:
        Subarray sum = pref[r] - pref[l]. Need last digit x and first digit x, i.e.
        the difference lies in [x*10^p, (x+1)*10^p - 1] and matches mod 10.

        Algorithm:
        - Keep prefix values grouped by residue mod 10 (sorted by construction).
        - For each new prefix R, for each digit-length bucket, count prior L in the
          corresponding interval with residue (R - x) mod 10 via binary search.

        Complexity: O(n log n * D) time with D ~ 15, O(n) space.
        """
        prefs = [[] for _ in range(10)]
        prefs[0].append(0)
        pref = ans = 0
        powers = [10**p for p in range(15)]
        for num in nums:
            pref += num
            need = (pref - x) % 10
            arr = prefs[need]
            for p in powers:
                lo_v = x * p
                hi_v = min((x + 1) * p - 1, pref)
                if lo_v > hi_v:
                    if lo_v > pref:
                        break
                    continue
                Llo = pref - hi_v
                Lhi = pref - lo_v
                ans += bisect_right(arr, Lhi) - bisect_left(arr, Llo)
            prefs[pref % 10].append(pref)
        return ans
# @lc code=end
