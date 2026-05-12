#
# @lc app=leetcode id=1282 lang=python3
#
# [1282] Group the People Given the Group Size They Belong To
#
# https://leetcode.com/problems/group-the-people-given-the-group-size-they-belong-to/description/
#
# algorithms
# Medium (87.49%)
# Likes:    3167
# Dislikes: 750
# Total Accepted:    251.7K
# Total Submissions: 287.7K
# Testcase Example:  '[3,3,3,3,3,1,3]'
#
# There are n people that are split into some unknown number of groups. Each
# person is labeled with a unique ID from 0 to n - 1.
# 
# You are given an integer array groupSizes, where groupSizes[i] is the size of
# the group that person i is in. For example, if groupSizes[1] = 3, then person
# 1 must be in a group of size 3.
# 
# Return a list of groups such that each person i is in a group of size
# groupSizes[i].
# 
# Each person should appear in exactly one group, and every person must be in a
# group. If there are multiple answers, return any of them. It is guaranteed
# that there will be at least one valid solution for the given input.
# 
# 
# Example 1:
# 
# 
# Input: groupSizes = [3,3,3,3,3,1,3]
# Output: [[5],[0,1,2],[3,4,6]]
# Explanation: 
# The first group is [5]. The size is 1, and groupSizes[5] = 1.
# The second group is [0,1,2]. The size is 3, and groupSizes[0] = groupSizes[1]
# = groupSizes[2] = 3.
# The third group is [3,4,6]. The size is 3, and groupSizes[3] = groupSizes[4]
# = groupSizes[6] = 3.
# Other possible solutions are [[2,1,6],[5],[0,4,3]] and
# [[5],[0,6,2],[4,3,1]].
# 
# 
# Example 2:
# 
# 
# Input: groupSizes = [2,1,3,3,3,2]
# Output: [[1],[0,5],[2,3,4]]
# 
# 
# 
# Constraints:
# 
# 
# groupSizes.length == n
# 1 <= n <= 500
# 1 <= groupSizes[i] <= n
# 
# 
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def groupThePeople(self, groupSizes: List[int]) -> List[List[int]]:
        buckets = defaultdict(list)
        groups = []

        for person, size in enumerate(groupSizes):
            buckets[size].append(person)
            if len(buckets[size]) == size:
                groups.append(buckets[size])
                buckets[size] = []

        return groups
# @lc code=end

# Explanation
# -----------
# Bucket people by their required group size. When a bucket reaches that size,
# it forms one complete group and is flushed to the answer.
#
# A dictionary from size to current partial group is sufficient because people
# with the same required size are interchangeable. The problem guarantees a
# valid arrangement exists.
#
# Edge cases: group size 1 flushes immediately; many groups of the same size;
# input order does not need to be preserved beyond valid grouping.
#
# Time complexity: O(n).
# Space complexity: O(n) for output and partial buckets.
