#
# @lc app=leetcode id=1257 lang=python3
#
# [1257] Smallest Common Region
#
# https://leetcode.com/problems/smallest-common-region/description/
#
# algorithms
# Medium (68.31%)
# Likes:    498
# Dislikes: 42
# Total Accepted:    38.1K
# Total Submissions: 55.7K
# Testcase Example:  '[["Earth","North America","South America"],["North America","United States","Canada"],["United States","New York","Boston"],["Canada","Ontario","Quebec"],["South America","Brazil"]]\n' +
# '"Quebec"\n' +
# '"New York"'
#
# You are given some lists of regions where the first region of each list
# directly contains all other regions in that list.
# 
# If a region x contains a region y directly, and region y contains region z
# directly, then region x is said to contain region z indirectly. Note that
# region x also indirectly contains all regions indirectly containd in y.
# 
# Naturally, if a region x contains (either directly or indirectly) another
# region y, then x is bigger than or equal to y in size. Also, by definition, a
# region x contains itself.
# 
# Given two regions: region1 and region2, return the smallest region that
# contains both of them.
# 
# It is guaranteed the smallest region exists.
# 
# 
# Example 1:
# 
# 
# Input:
# regions = [["Earth","North America","South America"],
# ["North America","United States","Canada"],
# ["United States","New York","Boston"],
# ["Canada","Ontario","Quebec"],
# ["South America","Brazil"]],
# region1 = "Quebec",
# region2 = "New York"
# Output: "North America"
# 
# 
# Example 2:
# 
# 
# Input: regions = [["Earth", "North America", "South America"],["North
# America", "United States", "Canada"],["United States", "New York",
# "Boston"],["Canada", "Ontario", "Quebec"],["South America", "Brazil"]],
# region1 = "Canada", region2 = "South America"
# Output: "Earth"
# 
# 
# 
# Constraints:
# 
# 
# 2 <= regions.length <= 10^4
# 2 <= regions[i].length <= 20
# 1 <= regions[i][j].length, region1.length, region2.length <= 20
# region1 != region2
# regions[i][j], region1, and region2 consist of English letters.
# The input is generated such that there exists a region which contains all the
# other regions, either directly or indirectly.
# A region cannot be directly contained in more than one region.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def findSmallestRegion(self, regions: List[List[str]], region1: str, region2: str) -> str:
        parent = {}
        for group in regions:
            root = group[0]
            for child in group[1:]:
                parent[child] = root

        ancestors = set()
        cur = region1
        while cur:
            ancestors.add(cur)
            cur = parent.get(cur)

        cur = region2
        while cur not in ancestors:
            cur = parent[cur]

        return cur
# @lc code=end

# Explanation
# -----------
# Treat the region hierarchy as a parent-pointer tree. Build child -> parent
# from the input lists. Add every ancestor of region1 to a set, then climb from
# region2 until reaching the first ancestor also in that set. That first match
# is the lowest common ancestor, which is the smallest common region.
#
# Parent pointers are sufficient because each region has exactly one parent in
# the hierarchy.
#
# Edge cases: one region is an ancestor of the other; both regions are the
# same; the answer may be the global root.
#
# Time complexity: O(N), where N is the number of region names.
# Space complexity: O(N) for parent map and ancestor set.
