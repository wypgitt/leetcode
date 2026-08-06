#
# @lc app=leetcode id=3845 lang=python3
#
# [3845] Maximum Subarray XOR with Bounded Range
#
# https://leetcode.com/problems/maximum-subarray-xor-with-bounded-range/description/
#
# algorithms
# Hard (33.41%)
# Likes:    70
# Dislikes: 3
# Total Accepted:    5.6K
# Total Submissions: 16.9K
# Testcase Example:  "[5,4,5,6]\n2"
#
#
# You are given a non-negative integer array nums and an integer k.
#
# You must select a subarray of nums such that the difference between its
# maximum and minimum elements is at most k. The value of this subarray is
# the bitwise XOR of all elements in the subarray.
#
# Return an integer denoting the maximum possible value of the selected
# subarray.
#
# Example 1:
#
# Input: nums = [5,4,5,6], k = 2
#
# Output: 7
#
# Explanation:
#
# Select the subarray [5, 4, 5, 6].
#
# The difference between its maximum and minimum elements is 6 - 4 = 2 <=
# k.
#
# The value is 4 XOR 5 XOR 6 = 7.
#
# Example 2:
#
# Input: nums = [5,4,5,6], k = 1
#
# Output: 6
#
# Explanation:
#
# Select the subarray [5, 4, 5, 6].
#
# The difference between its maximum and minimum elements is 6 - 6 = 0 <=
# k.
#
# The value is 6.
#
# Constraints:
#
# 1 <= nums.length <= 4 * 10^4
#
# 0 <= nums[i] < 2^15
#
# 0 <= k < 2^15
#

# @lc code=start
from collections import deque
from typing import List


class BinaryTrie:
    MAX_BIT = 14

    def __init__(self) -> None:
        """
        Interview explanation:
        Binary trie over 15-bit prefix XORs with occurrence counts for sliding
        window insert/delete and max-XOR queries.

        Algorithm:
        - Root node 0; each node stores two children and a live count.

        Complexity: O(1) init time/space.
        """
        self.child = [[-1, -1]]
        self.count = [0]

    def insert(self, value: int) -> None:
        """
        Interview explanation:
        Insert a prefix XOR into the trie.

        Algorithm:
        - Walk bits high-to-low, creating nodes and incrementing counts.

        Complexity: O(B) time with B=15, O(B) space amortized.
        """
        node = 0
        self.count[node] += 1
        for bit_index in range(self.MAX_BIT, -1, -1):
            bit = (value >> bit_index) & 1
            nxt = self.child[node][bit]
            if nxt == -1:
                nxt = len(self.child)
                self.child[node][bit] = nxt
                self.child.append([-1, -1])
                self.count.append(0)
            node = nxt
            self.count[node] += 1

    def remove(self, value: int) -> None:
        """
        Interview explanation:
        Remove one occurrence of a previously inserted prefix XOR.

        Algorithm:
        - Walk the same bit path and decrement counts.

        Complexity: O(B) time, O(1) space.
        """
        node = 0
        self.count[node] -= 1
        for bit_index in range(self.MAX_BIT, -1, -1):
            bit = (value >> bit_index) & 1
            node = self.child[node][bit]
            self.count[node] -= 1

    def max_xor(self, value: int) -> int:
        """
        Interview explanation:
        Maximum XOR of `value` against any live prefix in the trie.

        Algorithm:
        - Prefer the opposite bit at each level when that subtree is nonempty.

        Complexity: O(B) time, O(1) space.
        """
        node = 0
        best = 0
        for bit_index in range(self.MAX_BIT, -1, -1):
            bit = (value >> bit_index) & 1
            preferred = bit ^ 1
            preferred_node = self.child[node][preferred]

            if preferred_node != -1 and self.count[preferred_node] > 0:
                best |= 1 << bit_index
                node = preferred_node
            else:
                node = self.child[node][bit]

        return best


class Solution:
    def maxXor(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Maximize subarray XOR among subarrays whose max-min difference is <= k.
        Sliding window of valid ranges plus XOR-trie of prefix XORs.

        Algorithm:
        - Expand right; maintain deques for window max/min.
        - Shrink left while max - min > k, removing old prefixes from the trie.
        - Query max XOR of current prefix against prefixes in the window.

        Complexity: O(n B) time, O(n B) space.
        """
        trie = BinaryTrie()
        max_q = deque()
        min_q = deque()
        prefixes = [0]

        left = 0
        current_prefix = 0
        ans = 0

        for right, value in enumerate(nums):
            trie.insert(prefixes[right])

            while max_q and nums[max_q[-1]] <= value:
                max_q.pop()
            max_q.append(right)

            while min_q and nums[min_q[-1]] >= value:
                min_q.pop()
            min_q.append(right)

            while nums[max_q[0]] - nums[min_q[0]] > k:
                trie.remove(prefixes[left])
                if max_q[0] == left:
                    max_q.popleft()
                if min_q[0] == left:
                    min_q.popleft()
                left += 1

            current_prefix ^= value
            ans = max(ans, trie.max_xor(current_prefix))
            prefixes.append(current_prefix)

        return ans
# @lc code=end
