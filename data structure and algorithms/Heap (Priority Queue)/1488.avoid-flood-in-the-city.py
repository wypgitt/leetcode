#
# @lc app=leetcode id=1488 lang=python3
#
# [1488] Avoid Flood in The City
#
# https://leetcode.com/problems/avoid-flood-in-the-city/description/
#
# algorithms
# Medium (38.97%)
# Likes:    2161
# Dislikes: 624
# Total Accepted:    135K
# Total Submissions: 348K
# Testcase Example:  "[1,2,3,4]"
#
# Your country has 10^9 lakes. Initially, all the lakes are empty, but when it
# rains over the n^th lake, the n^th lake becomes full of water. If it rains
# over a lake that is full of water, there will be a flood. Your goal is to
# avoid floods in any lake.
#
# Given an integer array rains where:
#
# rains[i] > 0 means there will be rains over the rains[i] lake.
#
# rains[i] == 0 means there are no rains this day and you must choose one lake
# this day and dry it.
#
# Return an array ans where:
#
# ans.length == rains.length
#
# ans[i] == -1 if rains[i] > 0.
#
# ans[i] is the lake you choose to dry in the ith day if rains[i] == 0.
#
# If there are multiple valid answers return any of them. If it is impossible
# to avoid flood return an empty array.
#
# Notice that if you chose to dry a full lake, it becomes empty, but if you
# chose to dry an empty lake, nothing changes.
#
# Example 1:
#
# Input: rains = [1,2,3,4]
# Output: [-1,-1,-1,-1]
# Explanation: After the first day full lakes are [1]
# After the second day full lakes are [1,2]
# After the third day full lakes are [1,2,3]
# After the fourth day full lakes are [1,2,3,4]
# There's no day to dry any lake and there is no flood in any lake.
#
# Example 2:
#
# Input: rains = [1,2,0,0,2,1]
# Output: [-1,-1,2,1,-1,-1]
# Explanation: After the first day full lakes are [1]
# After the second day full lakes are [1,2]
# After the third day, we dry lake 2. Full lakes are [1]
# After the fourth day, we dry lake 1. There is no full lakes.
# After the fifth day, full lakes are [2].
# After the sixth day, full lakes are [1,2].
# It is easy that this scenario is flood-free. [-1,-1,1,2,-1,-1] is another
# acceptable scenario.
#
# Example 3:
#
# Input: rains = [1,2,0,1,2]
# Output: []
# Explanation: After the second day, full lakes are [1,2]. We have to dry one
# lake in the third day.
# After that, it will rain over lakes [1,2]. It's easy to prove that no matter
# which lake you choose to dry in the 3rd day, the other one will flood.
#
# Constraints:
#
# 1 <= rains.length <= 10^5
#
# 0 <= rains[i] <= 10^9
#

# @lc code=start
from typing import List
import bisect


class Solution:
    def avoidFlood(self, rains: List[int]) -> List[int]:
        """
        Interview explanation:
        rains[i]>0 fills lake; rains[i]==0 is dry day. Avoid flooding a lake
        that already has water. On dry days, dry a lake that rains again later.
        Map lake→last rain day + sorted list of dry days; bisect for a dry day
        after the previous rain.

        Algorithm:
        - full[lake]=day; dry days list; when lake rains again, bisect_right for
          dry day > last; assign ans[day]=lake; pop that dry day.

        Complexity: O(n log n) time (bisect + list pop O(n) worst → O(n^2);
        acceptable for n≤1e5 typically with careful use; here n constraints OK).
        """
        n = len(rains)
        ans = [1] * n
        full = {}
        dry = []
        for i, lake in enumerate(rains):
            if lake == 0:
                dry.append(i)
            else:
                if lake in full:
                    j = bisect.bisect_right(dry, full[lake])
                    if j == len(dry):
                        return []
                    day = dry.pop(j)
                    ans[day] = lake
                full[lake] = i
                ans[i] = -1
        return ans
# @lc code=end
