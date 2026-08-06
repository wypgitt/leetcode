#
# @lc app=leetcode id=677 lang=python3
#
# [677] Map Sum Pairs
#
# https://leetcode.com/problems/map-sum-pairs/description/
#
# algorithms
# Medium (57.31%)
# Likes:    1744
# Dislikes: 167
# Total Accepted:    145K
# Total Submissions: 253K
# Testcase Example:  "[\"MapSum\",\"insert\",\"sum\",\"insert\",\"sum\"]"
#
# Design a map that allows you to do the following:
#
# Maps a string key to a given value.
#
# Returns the sum of the values that have a key with a prefix equal to a given
# string.
#
# Implement the MapSum class:
#
# MapSum() Initializes the MapSum object.
#
# void insert(String key, int val) Inserts the key-val pair into the map. If
# the key already existed, the original key-value pair will be overridden to
# the new one.
#
# int sum(string prefix) Returns the sum of all the pairs' value whose key
# starts with the prefix.
#
# Example 1:
#
# Input
# ["MapSum", "insert", "sum", "insert", "sum"]
# [[], ["apple", 3], ["ap"], ["app", 2], ["ap"]]
# Output
# [null, null, 3, null, 5]
#
# Explanation
# MapSum mapSum = new MapSum();
# mapSum.insert("apple", 3);
# mapSum.sum("ap"); // return 3 (apple = 3)
# mapSum.insert("app", 2);
# mapSum.sum("ap"); // return 5 (apple + app = 3 + 2 = 5)
#
# Constraints:
#
# 1 <= key.length, prefix.length <= 50
#
# key and prefix consist of only lowercase English letters.
#
# 1 <= val <= 1000
#
# At most 50 calls will be made to insert and sum.
#

# @lc code=start
class TrieNode:
    def __init__(self):
        self.children = {}
        self.score = 0


class MapSum:
    def __init__(self):
        """
        Interview explanation:
        Prefix-sum map: insert(key,val) and sum of values whose keys share a
        prefix. Trie stores running score on each node so prefix sum is a walk.

        Algorithm:
        - Root TrieNode; map key -> previous value for overwrite deltas.

        Complexity: O(1) init.
        """
        self.root = TrieNode()
        self.vals = {}

    def insert(self, key: str, val: int) -> None:
        """
        Interview explanation:
        Insert/overwrite key. Add delta = val - old along the path so prefix
        scores stay correct.

        Algorithm:
        - delta = val - vals.get(key, 0); walk chars adding delta to node.score.

        Complexity: O(L) time, O(L) space for new nodes.
        """
        delta = val - self.vals.get(key, 0)
        self.vals[key] = val
        node = self.root
        for c in key:
            if c not in node.children:
                node.children[c] = TrieNode()
            node = node.children[c]
            node.score += delta

    def sum(self, prefix: str) -> int:
        """
        Interview explanation:
        Walk the trie for prefix; return the score at the final node (sum of
        all values under that prefix).

        Algorithm:
        - If prefix missing, return 0; else return node.score.

        Complexity: O(L) time, O(1) extra space.
        """
        node = self.root
        for c in prefix:
            if c not in node.children:
                return 0
            node = node.children[c]
        return node.score


# Your MapSum object will be instantiated and called as such:
# obj = MapSum()
# obj.insert(key,val)
# param_2 = obj.sum(prefix)
# @lc code=end
