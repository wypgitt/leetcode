#
# @lc app=leetcode id=1424 lang=python3
#
# [1424] Diagonal Traverse II
#
# https://leetcode.com/problems/diagonal-traverse-ii/description/
#
# algorithms
# Medium (58.34%)
# Likes:    2308
# Dislikes: 161
# Total Accepted:    181K
# Total Submissions: 310K
# Testcase Example:  "[[1,2,3],[4,5,6],[7,8,9]]"
#
# Given a 2D integer array nums, return all elements of nums in diagonal order
# as shown in the below images.
#
# Example 1:
#
# Input: nums = [[1,2,3],[4,5,6],[7,8,9]]
# Output: [1,4,2,7,5,3,8,6,9]
#
# Example 2:
#
# Input: nums = [[1,2,3,4,5],[6,7],[8],[9,10,11],[12,13,14,15,16]]
# Output: [1,6,2,8,7,3,9,4,12,10,5,13,11,14,15,16]
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i].length <= 10^5
#
# 1 <= sum(nums[i].length) <= 10^5
#
# 1 <= nums[i][j] <= 10^5
#

# @lc code=start
from typing import List
from collections import defaultdict, deque


class Solution:
    def findDiagonalOrder(self, nums: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Elements with same i+j lie on a diagonal; traverse diagonals in order
        of i+j, and within a diagonal from bottom-left to top-right (increasing i
        means later — actually problem wants decreasing row / increasing col order
        which is: group by i+j, append in reverse of discovery by rows).

        Algorithm:
        (group by i+j)
        - Map d=i+j → list of values in row order; for each d ascending, reverse list.

        Complexity: O(N) time and space for N total elements.
        """
        groups = defaultdict(list)
        for i, row in enumerate(nums):
            for j, v in enumerate(row):
                groups[i + j].append(v)
        ans = []
        for d in range(len(groups)):
            ans.extend(reversed(groups[d]))
        return ans

    def findDiagonalOrder_bfs(self, nums: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Alternate BFS: start (0,0); from (i,j) push (i+1,j) then (i,j+1) with a
        visited set — natural diagonal order for this problem.

        Algorithm:
        - Queue BFS; visit (r,c); append nums[r][c]; enqueue down then right if valid.

        Complexity: O(N) time and space.
        """
        if not nums:
            return []
        ans = []
        q = deque([(0, 0)])
        seen = {(0, 0)}
        while q:
            i, j = q.popleft()
            ans.append(nums[i][j])
            if i + 1 < len(nums) and j < len(nums[i + 1]) and (i + 1, j) not in seen:
                seen.add((i + 1, j))
                q.append((i + 1, j))
            if j + 1 < len(nums[i]) and (i, j + 1) not in seen:
                seen.add((i, j + 1))
                q.append((i, j + 1))
        return ans
# @lc code=end
