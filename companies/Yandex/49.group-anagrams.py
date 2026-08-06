#
# @lc app=leetcode id=49 lang=python3
#
# [49] Group Anagrams
#
# https://leetcode.com/problems/group-anagrams/description/
#
# algorithms
# Medium (72.55%)
# Likes:    22118
# Dislikes: 758
# Total Accepted:    4.7M
# Total Submissions: 6.5M
# Testcase Example:  '["eat","tea","tan","ate","nat","bat"]'
#
# Given an array of strings strs, group the anagrams together. You can return
# the answer in any order.
# 
# 
# Example 1:
# 
# 
# Input: strs = ["eat","tea","tan","ate","nat","bat"]
# 
# Output: [["bat"],["nat","tan"],["ate","eat","tea"]]
# 
# Explanation:
# 
# 
# There is no string in strs that can be rearranged to form "bat".
# The strings "nat" and "tan" are anagrams as they can be rearranged to form
# each other.
# The strings "ate", "eat", and "tea" are anagrams as they can be rearranged to
# form each other.
# 
# 
# 
# Example 2:
# 
# 
# Input: strs = [""]
# 
# Output: [[""]]
# 
# 
# Example 3:
# 
# 
# Input: strs = ["a"]
# 
# Output: [["a"]]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= strs.length <= 10^4
# 0 <= strs[i].length <= 100
# strs[i] consists of lowercase English letters.
# 
# 
#

# @lc code=start
from typing import List, Optional
from collections import defaultdict

class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        """
        Interview explanation:
        Anagrams share the same character multiset. For lowercase English words,
        a 26-count tuple is a canonical hashable key and avoids sorting each
        string. A dictionary groups words by that key.

        Edge cases and tests:
        - Empty string maps to all-zero counts.
        - Single-character strings group by that character.
        - Duplicate words remain as duplicate entries in their group.

        Complexity: O(total characters) time, O(number of strings * alphabet)
        key space plus output storage. Alphabet is fixed at 26.
        """
        groups = defaultdict(list)
        for word in strs:
            counts = [0] * 26
            for ch in word:
                counts[ord(ch) - ord('a')] += 1
            groups[tuple(counts)].append(word)
        return list(groups.values())
# @lc code=end


