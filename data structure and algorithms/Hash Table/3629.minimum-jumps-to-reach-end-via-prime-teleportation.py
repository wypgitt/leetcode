#
# @lc app=leetcode id=3629 lang=python3
#
# [3629] Minimum Jumps to Reach End via Prime Teleportation
#
# https://leetcode.com/problems/minimum-jumps-to-reach-end-via-prime-teleportation/description/
#
# algorithms
# Medium (44.54%)
# Likes:    396
# Dislikes: 56
# Total Accepted:    90.4K
# Total Submissions: 202.9K
# Testcase Example:  "[1,2,4,6]"
#
#
# You are given an integer array nums of length n.
#
# You start at index 0, and your goal is to reach index n - 1.
#
# From any index i, you may perform one of the following operations:
#
# Adjacent Step: Jump to index i + 1 or i - 1, if the index is within
# bounds.
#
# Prime Teleportation: If nums[i] is a prime number p, you may instantly
# jump to any index j != i such that nums[j] % p == 0.
#
# Return the minimum number of jumps required to reach index n - 1.
#
# Example 1:
#
# Input: nums = [1,2,4,6]
#
# Output: 2
#
# Explanation:
#
# One optimal sequence of jumps is:
#
# Start at index i = 0. Take an adjacent step to index 1.
#
# At index i = 1, nums[1] = 2 is a prime number. Therefore, we teleport to
# index i = 3 as nums[3] = 6 is divisible by 2.
#
# Thus, the answer is 2.
#
# Example 2:
#
# Input: nums = [2,3,4,7,9]
#
# Output: 2
#
# Explanation:
#
# One optimal sequence of jumps is:
#
# Start at index i = 0. Take an adjacent step to index i = 1.
#
# At index i = 1, nums[1] = 3 is a prime number. Therefore, we teleport to
# index i = 4 since nums[4] = 9 is divisible by 3.
#
# Thus, the answer is 2.
#
# Example 3:
#
# Input: nums = [4,6,5,8]
#
# Output: 3
#
# Explanation:
#
# Since no teleportation is possible, we move through 0 → 1 → 2 → 3. Thus,
# the answer is 3.
#
# Constraints:
#
# 1 <= n == nums.length <= 10^5
#
# 1 <= nums[i] <= 10^6
#

# @lc code=start

from collections import defaultdict, deque
from typing import List


class Solution:
    def minJumps(self, nums: List[int]) -> int:
        """
        Interview explanation:
        BFS from index 0. Edges are +/-1 neighbors, plus from a prime index i
        teleport to any j with nums[j] % nums[i] == 0.

        Algorithm:
        - Factor each value via SPF; map each prime p -> indices divisible by p.
        - BFS; when at prime p, enqueue all adj[p] once, then clear that list
          so each prime teleport set is used O(1) times.

        Complexity: O(n log A + A) time with sieve, O(A + n) space.
        """
        adj = defaultdict(list)
        for i, x in enumerate(nums):
            while x != 1:
                p = self._SPF[x]
                while x % p == 0:
                    x //= p
                adj[p].append(i)

        n = len(nums)
        dist = [-1] * n
        dist[0] = 0
        q = deque([0])
        while q:
            i = q.popleft()
            if i == n - 1:
                return dist[i]
            for ni in (i - 1, i + 1):
                if 0 <= ni < n and dist[ni] == -1:
                    dist[ni] = dist[i] + 1
                    q.append(ni)
            p = nums[i]
            if self._SPF[p] == p and p in adj:
                for ni in adj[p]:
                    if dist[ni] == -1:
                        dist[ni] = dist[i] + 1
                        q.append(ni)
                del adj[p]
        return -1


def _linear_sieve(limit: int):
    primes = []
    spf = [-1] * (limit + 1)
    for i in range(2, limit + 1):
        if spf[i] == -1:
            spf[i] = i
            primes.append(i)
        for p in primes:
            if i * p > limit or p > spf[i]:
                break
            spf[i * p] = p
    return spf


Solution._SPF = _linear_sieve(10**6)
# @lc code=end

