#
# @lc app=leetcode id=760 lang=python3
#
# [760] Find Anagram Mappings
#
# https://leetcode.com/problems/find-anagram-mappings/description/
#
# algorithms
# Easy (83.99%)
# Likes:    624
# Dislikes: 235
# Total Accepted:    113.5K
# Total Submissions: 135.1K
# Testcase Example:  "[12,28,46,32,50]\n[50,12,32,46,28]"
#
#
# You are given two integer arrays nums1 and nums2 where nums2 is an
# anagram of nums1. Both arrays may contain duplicates.
#
# Return an index mapping array mapping from nums1 to nums2 where
# mapping[i] = j means the i^th element in nums1 appears in nums2 at index
# j. If there are multiple answers, return any of them.
#
# An array a is an anagram of an array b means b is made by randomizing
# the order of the elements in a.
#
# Example 1:
#
# Input: nums1 = [12,28,46,32,50], nums2 = [50,12,32,46,28]
# Output: [1,4,3,2,0]
# Explanation: As mapping[0] = 1 because the 0^th element of nums1 appears
# at nums2[1], and mapping[1] = 4 because the 1^st element of nums1
# appears at nums2[4], and so on.
#
# Example 2:
#
# Input: nums1 = [84,46], nums2 = [84,46]
# Output: [0,1]
#
# Constraints:
#
# 1 <= nums1.length <= 100
#
# nums2.length == nums1.length
#
# 0 <= nums1[i], nums2[i] <= 10^5
#
# nums2 is an anagram of nums1.
#
# @lc code=start
from collections import defaultdict
from typing import Dict, List


class Solution:
    def anagramMappings(self, nums1: List[int], nums2: List[int]) -> List[int]:
        """
        Interview explanation:
        Premium. nums1 is an anagram of nums2; return any mapping where
        nums1[i] = nums2[mapping[i]]. Index nums2 values to lists of indices.

        Algorithm:
        - Map value -> list of indices in nums2
        - For each x in nums1: pop an index from the map

        Complexity: O(n) time and space.
        """
        pos: Dict[int, List[int]] = defaultdict(list)
        for i, x in enumerate(nums2):
            pos[x].append(i)
        return [pos[x].pop() for x in nums1]
# @lc code=end

