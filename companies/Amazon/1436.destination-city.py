#
# @lc app=leetcode id=1436 lang=python3
#
# [1436] Destination City
#
# https://leetcode.com/problems/destination-city/description/
#
# algorithms
# Easy (79.54%)
# Likes:    2331
# Dislikes: 108
# Total Accepted:    333K
# Total Submissions: 419K
# Testcase Example:  "[[\"London\",\"New York\"],[\"New York\",\"Lima\"],[\"Lima\",\"Sao Paulo\"]]"
#
# You are given the array paths, where paths[i] = [cityA_i, cityB_i] means
# there exists a direct path going from cityA_i to cityB_i. Return the
# destination city, that is, the city without any path outgoing to another
# city.
#
# It is guaranteed that the graph of paths forms a line without any loop,
# therefore, there will be exactly one destination city.
#
# Example 1:
#
# Input: paths = [["London","New York"],["New York","Lima"],["Lima","Sao
# Paulo"]]
# Output: "Sao Paulo"
# Explanation: Starting at "London" city you will reach "Sao Paulo" city which
# is the destination city. Your trip consist of: "London" -> "New York" ->
# "Lima" -> "Sao Paulo".
#
# Example 2:
#
# Input: paths = [["B","C"],["D","B"],["C","A"]]
# Output: "A"
# Explanation: All possible trips are:
# "D" -> "B" -> "C" -> "A".
# "B" -> "C" -> "A".
# "C" -> "A".
# "A".
# Clearly the destination city is "A".
#
# Example 3:
#
# Input: paths = [["A","Z"]]
# Output: "Z"
#
# Constraints:
#
# 1 <= paths.length <= 100
#
# paths[i].length == 2
#
# 1 <= cityA_i.length, cityB_i.length <= 10
#
# cityA_i != cityB_i
#
# All strings consist of lowercase and uppercase English letters and the space
# character.
#

# @lc code=start
from typing import List


class Solution:
    def destCity(self, paths: List[List[str]]) -> str:
        """
        Interview explanation:
        Paths form a line; destination is city that never appears as a start.

        Algorithm:
        (set)
        - starts={a for a,b in paths}; return b where b not in starts.

        Complexity: O(n) time, O(n) space.
        """
        starts = {a for a, _ in paths}
        for _, b in paths:
            if b not in starts:
                return b
        return ""

    def destCity_counter(self, paths: List[List[str]]) -> str:
        """
        Interview explanation:
        Alternate: degree / outgoing count; city with outdegree 0 is destination.

        Algorithm:
        - out count for starts; find end with out==0.

        Complexity: O(n) time, O(n) space.
        """
        out = {}
        cities = set()
        for a, b in paths:
            out[a] = out.get(a, 0) + 1
            out.setdefault(b, 0)
            cities.add(a)
            cities.add(b)
        for c in cities:
            if out.get(c, 0) == 0:
                return c
        return ""
# @lc code=end
