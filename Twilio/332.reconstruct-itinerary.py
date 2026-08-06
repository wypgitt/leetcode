#
# @lc app=leetcode id=332 lang=python3
#
# [332] Reconstruct Itinerary
#
# https://leetcode.com/problems/reconstruct-itinerary/description/
#
# algorithms
# Hard (44.85%)
# Likes:    6387
# Dislikes: 1931
# Total Accepted:    569K
# Total Submissions: 1.3M
# Testcase Example:  "[[\"MUC\",\"LHR\"],[\"JFK\",\"MUC\"],[\"SFO\",\"SJC\"],[\"LHR\",\"SFO\"]]"
#
# You are given a list of airline tickets where tickets[i] = [from_i, to_i]
# represent the departure and the arrival airports of one flight. Reconstruct
# the itinerary in order and return it.
#
# All of the tickets belong to a man who departs from "JFK", thus, the
# itinerary must begin with "JFK". If there are multiple valid itineraries, you
# should return the itinerary that has the smallest lexical order when read as
# a single string.
#
# For example, the itinerary ["JFK", "LGA"] has a smaller lexical order than
# ["JFK", "LGB"].
#
# You may assume all tickets form at least one valid itinerary. You must use
# all the tickets once and only once.
#
# Example 1:
#
# Input: tickets = [["MUC","LHR"],["JFK","MUC"],["SFO","SJC"],["LHR","SFO"]]
# Output: ["JFK","MUC","LHR","SFO","SJC"]
#
# Example 2:
#
# Input: tickets =
# [["JFK","SFO"],["JFK","ATL"],["SFO","ATL"],["ATL","JFK"],["ATL","SFO"]]
# Output: ["JFK","ATL","JFK","SFO","ATL","SFO"]
# Explanation: Another possible reconstruction is
# ["JFK","SFO","ATL","JFK","ATL","SFO"] but it is larger in lexical order.
#
# Constraints:
#
# 1 <= tickets.length <= 300
#
# tickets[i].length == 2
#
# from_i.length == 3
#
# to_i.length == 3
#
# from_i and to_i consist of uppercase English letters.
#
# from_i != to_i
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def findItinerary(self, tickets: List[List[str]]) -> List[str]:
        """
        Interview explanation:
        Hierholzer's algorithm for Eulerian path in a directed multigraph.
        Always take the lexicographically smallest unused edge (min-heap /
        sorted adjacency); post-order DFS yields the path reversed.

        Algorithm:
        - Build graph: dest lists sorted reverse so pop() gives smallest.
        - DFS from "JFK": while edges remain, recurse on pop(); then append.
        - Reverse the post-order list for the itinerary.

        Complexity: O(E log E) time (sorting), O(E) space.
        """
        graph = defaultdict(list)
        for a, b in sorted(tickets, reverse=True):
            graph[a].append(b)

        route: List[str] = []

        def dfs(airport: str) -> None:
            while graph[airport]:
                dfs(graph[airport].pop())
            route.append(airport)

        dfs("JFK")
        return route[::-1]
# @lc code=end
