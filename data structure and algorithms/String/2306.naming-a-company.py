#
# @lc app=leetcode id=2306 lang=python3
#
# [2306] Naming a Company
#
# https://leetcode.com/problems/naming-a-company/description/
#
# algorithms
# Hard (46.54%)
# Likes:    1968
# Dislikes: 74
# Total Accepted:    66.2K
# Total Submissions: 142.3K
# Testcase Example:  "[\"coffee\",\"donuts\",\"time\",\"toffee\"]"
#
# You are given an array of strings ideas that represents a list of names to be
# used in the process of naming a company. The process of naming a company is as
# follows:
#
#
# Choose 2 distinct names from ideas, call them idea_A and idea_B.
#
#
# Swap the first letters of idea_A and idea_B with each other.
#
#
# If both of the new names are not found in the original ideas, then the name
# idea_A idea_B (the concatenation of idea_A and idea_B, separated by a space)
# is a valid company name.
#
#
# Otherwise, it is not a valid name.
#
# Return the number of distinct valid names for the company.
#
#
#
# Example 1:
#
# Input: ideas = ["coffee","donuts","time","toffee"]
# Output: 6
# Explanation: The following selections are valid:
# - ("coffee", "donuts"): The company name created is "doffee conuts".
# - ("donuts", "coffee"): The company name created is "conuts doffee".
# - ("donuts", "time"): The company name created is "tonuts dime".
# - ("donuts", "toffee"): The company name created is "tonuts doffee".
# - ("time", "donuts"): The company name created is "dime tonuts".
# - ("toffee", "donuts"): The company name created is "doffee tonuts".
# Therefore, there are a total of 6 distinct company names.
#
# The following are some examples of invalid selections:
# - ("coffee", "time"): The name "toffee" formed after swapping already exists
# in the original array.
# - ("time", "toffee"): Both names are still the same after swapping and exist
# in the original array.
# - ("coffee", "toffee"): Both names formed after swapping already exist in the
# original array.
#
# Example 2:
#
# Input: ideas = ["lack","back"]
# Output: 0
# Explanation: There are no valid selections. Therefore, 0 is returned.
#
#
#
# Constraints:
#
#
# 2 <= ideas.length <= 5 * 10^4
#
#
# 1 <= ideas[i].length <= 10
#
#
# ideas[i] consists of lowercase English letters.
#
#
# All the strings in ideas are unique.
#

# @lc code=start
from typing import List
class Solution:
    def distinctNames(self, ideas: List[str]) -> int:
        """
        Interview explanation:
        Count valid company names formed by swapping first letters of two
        distinct ideas such that both results are not already ideas.

        Algorithm:
        - Group idea suffixes by first letter into sets.
        - For every pair of letters a,b: count suffixes exclusive to a and to
          b; contribute 2 * exclusives_a * exclusives_b.

        Complexity: O(n * L + 26^2 * avg_set) time; O(n) space.
        """
        groups = [set() for _ in range(26)]
        for w in ideas:
            groups[ord(w[0]) - 97].add(w[1:])
        ans = 0
        for i in range(26):
            for j in range(i + 1, 26):
                inter = len(groups[i] & groups[j])
                a = len(groups[i]) - inter
                b = len(groups[j]) - inter
                ans += 2 * a * b
        return ans
# @lc code=end
