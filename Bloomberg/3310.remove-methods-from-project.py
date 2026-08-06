#
# @lc app=leetcode id=3310 lang=python3
#
# [3310] Remove Methods From Project
#
# https://leetcode.com/problems/remove-methods-from-project/description/
#
# algorithms
# Medium (70.28%)
# Likes:    439
# Dislikes: 143
# Total Accepted:    125.9K
# Total Submissions: 179.1K
# Testcase Example:  "4\n1\n[[1,2],[0,1],[3,2]]"
#
#
# You are maintaining a project that has n methods numbered from 0 to n -
# 1.
#
# You are given two integers n and k, and a 2D integer array invocations,
# where invocations[i] = [a_i, b_i] indicates that method a_i invokes
# method b_i.
#
# There is a known bug in method k. Method k, along with any method
# invoked by it, either directly or indirectly, are considered suspicious
# and we aim to remove them.
#
# A group of methods can only be removed if no method outside the group
# invokes any methods within it.
#
# Return an array containing all the remaining methods after removing all
# the suspicious methods. You may return the answer in any order. If it is
# not possible to remove all the suspicious methods, none should be
# removed.
#
# Example 1:
#
# Input: n = 4, k = 1, invocations = [[1,2],[0,1],[3,2]]
#
# Output: [0,1,2,3]
#
# Explanation:
#
# Method 2 and method 1 are suspicious, but they are directly invoked by
# methods 3 and 0, which are not suspicious. We return all elements
# without removing anything.
#
# Example 2:
#
# Input: n = 5, k = 0, invocations = [[1,2],[0,2],[0,1],[3,4]]
#
# Output: [3,4]
#
# Explanation:
#
# Methods 0, 1, and 2 are suspicious and they are not directly invoked by
# any other method. We can remove them.
#
# Example 3:
#
# Input: n = 3, k = 2, invocations = [[1,2],[0,1],[2,0]]
#
# Output: []
#
# Explanation:
#
# All methods are suspicious. We can remove them.
#
# Constraints:
#
# 1 <= n <= 10^5
#
# 0 <= k <= n - 1
#
# 0 <= invocations.length <= 2 * 10^5
#
# invocations[i] == [a_i, b_i]
#
# 0 <= a_i, b_i <= n - 1
#
# a_i != b_i
#
# invocations[i] != invocations[j]
#

# @lc code=start
from collections import defaultdict, deque
from typing import List


class Solution:
    def remainingMethods(
        self, n: int, k: int, invocations: List[List[int]]
    ) -> List[int]:
        """
        Interview explanation:
        Suspicious = method k and everything reachable via invocations. Remove
        that set only if nothing outside invokes into it; otherwise keep all.

        Algorithm:
        - BFS/DFS from k on the invocation digraph to mark suspicious.
        - If any edge outside -> suspicious exists, return [0..n-1].
        - Else return non-suspicious methods.

        Complexity: O(n + m) time, O(n + m) space.
        """
        g: dict[int, list[int]] = defaultdict(list)
        for a, b in invocations:
            g[a].append(b)

        suspicious = {k}
        q = deque([k])
        while q:
            u = q.popleft()
            for v in g[u]:
                if v not in suspicious:
                    suspicious.add(v)
                    q.append(v)

        for a, b in invocations:
            if a not in suspicious and b in suspicious:
                return list(range(n))
        return [i for i in range(n) if i not in suspicious]
# @lc code=end
