#
# @lc app=leetcode id=599 lang=python3
#
# [599] Minimum Index Sum of Two Lists
#
# https://leetcode.com/problems/minimum-index-sum-of-two-lists/description/
#
# algorithms
# Easy (60.27%)
# Likes:    2128
# Dislikes: 418
# Total Accepted:    327K
# Total Submissions: 542K
# Testcase Example:  "[\"Shogun\",\"Tapioca Express\",\"Burger King\",\"KFC\"]"
#
# Given two arrays of strings list1 and list2, find the common strings with the
# least index sum.
#
# A common string is a string that appeared in both list1 and list2.
#
# A common string with the least index sum is a common string such that if it
# appeared at list1[i] and list2[j] then i + j should be the minimum value
# among all the other common strings.
#
# Return all the common strings with the least index sum. Return the answer in
# any order.
#
# Example 1:
#
# Input: list1 = ["Shogun","Tapioca Express","Burger King","KFC"], list2 =
# ["Piatti","The Grill at Torrey Pines","Hungry Hunter Steakhouse","Shogun"]
# Output: ["Shogun"]
# Explanation: The only common string is "Shogun".
#
# Example 2:
#
# Input: list1 = ["Shogun","Tapioca Express","Burger King","KFC"], list2 =
# ["KFC","Shogun","Burger King"]
# Output: ["Shogun"]
# Explanation: The common string with the least index sum is "Shogun" with
# index sum = (0 + 1) = 1.
#
# Example 3:
#
# Input: list1 = ["happy","sad","good"], list2 = ["sad","happy","good"]
# Output: ["sad","happy"]
# Explanation: There are three common strings:
# "happy" with index sum = (0 + 1) = 1.
# "sad" with index sum = (1 + 0) = 1.
# "good" with index sum = (2 + 2) = 4.
# The strings with the least index sum are "sad" and "happy".
#
# Constraints:
#
# 1 <= list1.length, list2.length <= 1000
#
# 1 <= list1[i].length, list2[i].length <= 30
#
# list1[i] and list2[i] consist of spaces ' ' and English letters.
#
# All the strings of list1 are unique.
#
# All the strings of list2 are unique.
#
# There is at least a common string between list1 and list2.
#


# @lc code=start
from typing import Dict, List
class Solution:
    def findRestaurant(self, list1: List[str], list2: List[str]) -> List[str]:
        """
        Interview explanation:
        Common strings are candidates; among them minimize index1 + index2.
        Hash list1 indices, scan list2, track the best sum and all ties.

        Algorithm:
        - index = {name: i for i, name in enumerate(list1)}.
        - For each j, name in list2: if name in index, s = index[name]+j;
          update ans when s is smaller / equal.

        Complexity: O(L1 + L2) time, O(L1) space.
        """
        index: Dict[str, int] = {name: i for i, name in enumerate(list1)}
        best = float("inf")
        ans: List[str] = []
        for j, name in enumerate(list2):
            if name not in index:
                continue
            s = index[name] + j
            if s < best:
                best = s
                ans = [name]
            elif s == best:
                ans.append(name)
        return ans
# @lc code=end

