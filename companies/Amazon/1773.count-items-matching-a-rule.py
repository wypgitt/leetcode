#
# @lc app=leetcode id=1773 lang=python3
#
# [1773] Count Items Matching a Rule
#
# https://leetcode.com/problems/count-items-matching-a-rule/description/
#
# algorithms
# Easy (85.4%)
# Likes:    2060
# Dislikes: 293
# Total Accepted:    294K
# Total Submissions: 344K
# Testcase Example:  "[[\"phone\",\"blue\",\"pixel\"],[\"computer\",\"silver\",\"lenovo\"],[\"phone\",\"gold\",\"iphone\"]]"
#
# You are given an array items, where each items[i] = [type_i, color_i, name_i]
# describes the type, color, and name of the i^th item. You are also given a
# rule represented by two strings, ruleKey and ruleValue.
#
# The i^th item is said to match the rule if one of the following is true:
#
# ruleKey == "type" and ruleValue == type_i.
#
# ruleKey == "color" and ruleValue == color_i.
#
# ruleKey == "name" and ruleValue == name_i.
#
# Return the number of items that match the given rule.
#
# Example 1:
#
# Input: items =
# [["phone","blue","pixel"],["computer","silver","lenovo"],["phone","gold","iphone"]],
# ruleKey = "color", ruleValue = "silver"
# Output: 1
# Explanation: There is only one item matching the given rule, which is
# ["computer","silver","lenovo"].
#
# Example 2:
#
# Input: items =
# [["phone","blue","pixel"],["computer","silver","phone"],["phone","gold","iphone"]],
# ruleKey = "type", ruleValue = "phone"
# Output: 2
# Explanation: There are only two items matching the given rule, which are
# ["phone","blue","pixel"] and ["phone","gold","iphone"]. Note that the item
# ["computer","silver","phone"] does not match.
#
# Constraints:
#
# 1 <= items.length <= 10^4
#
# 1 <= type_i.length, color_i.length, name_i.length, ruleValue.length <= 10
#
# ruleKey is equal to either "type", "color", or "name".
#
# All strings consist only of lowercase letters.
#

# @lc code=start
from typing import List


class Solution:
    def countMatches(self, items: List[List[str]], ruleKey: str, ruleValue: str) -> int:
        """
        Interview explanation:
        Each item is [type, color, name]. Count items whose field ruleKey
        equals ruleValue.

        Algorithm:
        - Map ruleKey → index {type:0,color:1,name:2}; count item[idx]==ruleValue.

        Complexity: O(n) time, O(1) space.
        """
        idx = {"type": 0, "color": 1, "name": 2}[ruleKey]
        return sum(item[idx] == ruleValue for item in items)

    def countMatches_if(self, items: List[List[str]], ruleKey: str, ruleValue: str) -> int:
        """
        Interview explanation:
        Alternate explicit branching on ruleKey without a dict map.

        Algorithm:
        - if/elif on ruleKey; compare corresponding field.

        Complexity: O(n).
        """
        ans = 0
        for t, c, n in items:
            if (ruleKey == "type" and t == ruleValue) or (
                ruleKey == "color" and c == ruleValue
            ) or (ruleKey == "name" and n == ruleValue):
                ans += 1
        return ans
# @lc code=end
