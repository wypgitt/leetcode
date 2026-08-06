#
# @lc app=leetcode id=3132 lang=python3
#
# [3132] Find the Integer Added to Array II
#
# https://leetcode.com/problems/find-the-integer-added-to-array-ii/description/
#
# algorithms
# Medium (33.00%)
# Likes:    182
# Dislikes: 44
# Total Accepted:    27K
# Total Submissions: 81.7K
# Testcase Example:  "[4,20,16,12,8]\n[14,18,10]"
#
#
# You are given two integer arrays nums1 and nums2.
#
# From nums1 two elements have been removed, and all other elements have
# been increased (or decreased in the case of negative) by an integer,
# represented by the variable x.
#
# As a result, nums1 becomes equal to nums2. Two arrays are considered
# equal when they contain the same integers with the same frequencies.
#
# Return the minimum possible integer x that achieves this equivalence.
#
# Example 1:
#
# Input: nums1 = [4,20,16,12,8], nums2 = [14,18,10]
#
# Output: -2
#
# Explanation:
#
# After removing elements at indices [0,4] and adding -2, nums1 becomes
# [18,14,10].
#
# Example 2:
#
# Input: nums1 = [3,5,5,3], nums2 = [7,7]
#
# Output: 2
#
# Explanation:
#
# After removing elements at indices [0,3] and adding 2, nums1 becomes
# [7,7].
#
# Constraints:
#
# 3 <= nums1.length <= 200
#
# nums2.length == nums1.length - 2
#
# 0 <= nums1[i], nums2[i] <= 1000
#
# The test cases are generated in a way that there is an integer x such
# that nums1 can become equal to nums2 by removing two elements and adding
# x to each element of nums1.
#

# @lc code=start
from typing import List


class Solution:
    def minimumAddedInteger(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        After removing two elements from nums1 and adding x to the rest, the
        multiset equals nums2. Return the minimum possible x.

        Algorithm:
        - Sort both. Candidate x values are nums2[0]-nums1[i] for i in {0,1,2}
          (at most two removals before the first kept match).
        - For each candidate, two-pointer check that nums1+x covers nums2 with
          at most two skips; take the minimum valid x.

        Complexity: O(n log n) time, O(n) space.
        """
        nums1 = sorted(nums1)
        nums2 = sorted(nums2)
        ans = 10**9

        def ok(x: int) -> bool:
            j = 0
            skips = 0
            for a in nums1:
                if j < len(nums2) and a + x == nums2[j]:
                    j += 1
                else:
                    skips += 1
                    if skips > 2:
                        return False
            return j == len(nums2)

        for i in range(3):
            x = nums2[0] - nums1[i]
            if ok(x):
                ans = min(ans, x)
        return ans
# @lc code=end
