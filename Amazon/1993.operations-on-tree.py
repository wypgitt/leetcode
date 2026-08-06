#
# @lc app=leetcode id=1993 lang=python3
#
# [1993] Operations on Tree
#
# https://leetcode.com/problems/operations-on-tree/description/
#
# algorithms
# Medium (45.71%)
# Likes:    525
# Dislikes: 85
# Total Accepted:    26.1K
# Total Submissions: 57.1K
# Testcase Example:  "[\"LockingTree\",\"lock\",\"unlock\",\"unlock\",\"lock\",\"upgrade\",\"lock\"]"
#
# You are given a tree with n nodes numbered from 0 to n - 1 in the form of a
# parent array parent where parent[i] is the parent of the i^th node. The root
# of the tree is node 0, so parent[0] = -1 since it has no parent. You want to
# design a data structure that allows users to lock, unlock, and upgrade nodes
# in the tree.
#
# The data structure should support the following functions:
#
# Lock: Locks the given node for the given user and prevents other users from
# locking the same node. You may only lock a node using this function if the
# node is unlocked.
#
# Unlock: Unlocks the given node for the given user. You may only unlock a node
# using this function if it is currently locked by the same user.
#
# Upgrade: Locks the given node for the given user and unlocks all of its
# descendants regardless of who locked it. You may only upgrade a node if all 3
# conditions are true:
#
# The node is unlocked,
#
# It has at least one locked descendant (by any user), and
#
# It does not have any locked ancestors.
#
# Implement the LockingTree class:
#
# LockingTree(int[] parent) initializes the data structure with the parent
# array.
#
# lock(int num, int user) returns true if it is possible for the user with id
# user to lock the node num, or false otherwise. If it is possible, the node
# num will become locked by the user with id user.
#
# unlock(int num, int user) returns true if it is possible for the user with id
# user to unlock the node num, or false otherwise. If it is possible, the node
# num will become unlocked.
#
# upgrade(int num, int user) returns true if it is possible for the user with
# id user to upgrade the node num, or false otherwise. If it is possible, the
# node num will be upgraded.
#
# Example 1:
#
# Input
# ["LockingTree", "lock", "unlock", "unlock", "lock", "upgrade", "lock"]
# [[[-1, 0, 0, 1, 1, 2, 2]], [2, 2], [2, 3], [2, 2], [4, 5], [0, 1], [0, 1]]
# Output
# [null, true, false, true, true, true, false]
#
# Explanation
# LockingTree lockingTree = new LockingTree([-1, 0, 0, 1, 1, 2, 2]);
# lockingTree.lock(2, 2); // return true because node 2 is unlocked.
# // Node 2 will now be locked by user 2.
# lockingTree.unlock(2, 3); // return false because user 3 cannot unlock a node
# locked by user 2.
# lockingTree.unlock(2, 2); // return true because node 2 was previously locked
# by user 2.
# // Node 2 will now be unlocked.
# lockingTree.lock(4, 5); // return true because node 4 is unlocked.
# // Node 4 will now be locked by user 5.
# lockingTree.upgrade(0, 1); // return true because node 0 is unlocked and has
# at least one locked descendant (node 4).
# // Node 0 will now be locked by user 1 and node 4 will now be unlocked.
# lockingTree.lock(0, 1); // return false because node 0 is already locked.
#
# Constraints:
#
# n == parent.length
#
# 2 <= n <= 2000
#
# 0 <= parent[i] <= n - 1 for i != 0
#
# parent[0] == -1
#
# 0 <= num <= n - 1
#
# 1 <= user <= 10^4
#
# parent represents a valid tree.
#
# At most 2000 calls in total will be made to lock, unlock, and upgrade.
#

# @lc code=start
from typing import List
from collections import defaultdict, deque


class LockingTree:
    def __init__(self, parent: List[int]):
        """
        Interview explanation:
        Design LockingTree: lock/unlock by user; upgrade locks a node and
        unlocks all locked descendants if node unlocked, has a locked
        descendant, and no locked ancestor.

        Algorithm:
        - Store parent[]; build children adjacency; locked[i]=user or 0 if free.

        Complexity: O(n) init time/space.
        """
        self.parent = parent
        self.locked = [0] * len(parent)
        self.children = defaultdict(list)
        for i, p in enumerate(parent):
            if p != -1:
                self.children[p].append(i)

    def lock(self, num: int, user: int) -> bool:
        """
        Interview explanation:
        Lock node num for user only if currently unlocked.

        Algorithm:
        - If locked[num]==0: set to user; return True; else False.

        Complexity: O(1).
        """
        if self.locked[num] == 0:
            self.locked[num] = user
            return True
        return False

    def unlock(self, num: int, user: int) -> bool:
        """
        Interview explanation:
        Unlock only if locked by the same user.

        Algorithm:
        - If locked[num]==user: clear to 0; return True; else False.

        Complexity: O(1).
        """
        if self.locked[num] == user:
            self.locked[num] = 0
            return True
        return False

    def upgrade(self, num: int, user: int) -> bool:
        """
        Interview explanation:
        Upgrade succeeds if num unlocked, no locked ancestor, and at least one
        locked descendant. Then lock num for user and unlock all descendants.

        Algorithm:
        - Walk parents for locked ancestors; BFS/DFS descendants for any lock;
          if ok, lock num and zero all descendant locks.

        Complexity: O(n) per call worst-case.
        """
        if self.locked[num] != 0:
            return False
        p = self.parent[num]
        while p != -1:
            if self.locked[p] != 0:
                return False
            p = self.parent[p]
        # find and unlock locked descendants
        q = deque(self.children[num])
        saw = False
        while q:
            u = q.popleft()
            if self.locked[u]:
                saw = True
                self.locked[u] = 0
            q.extend(self.children[u])
        if not saw:
            return False
        self.locked[num] = user
        return True


class LockingTreeDFS:
    """Alternate: DFS for descendant scan instead of BFS."""

    def __init__(self, parent: List[int]):
        """
        Interview explanation:
        Same tree locking API; children lists + locked array.

        Algorithm:
        - Build children from parent.

        Complexity: O(n) init.
        """
        self.parent = parent
        self.locked = [0] * len(parent)
        self.children = [[] for _ in range(len(parent))]
        for i, p in enumerate(parent):
            if p != -1:
                self.children[p].append(i)

    def lock(self, num: int, user: int) -> bool:
        """
        Interview explanation:
        Lock if unlocked.

        Algorithm:
        - locked[num] = user if free.

        Complexity: O(1).
        """
        if self.locked[num]:
            return False
        self.locked[num] = user
        return True

    def unlock(self, num: int, user: int) -> bool:
        """
        Interview explanation:
        Unlock if same user.

        Algorithm:
        - Clear locked[num] when matches user.

        Complexity: O(1).
        """
        if self.locked[num] != user:
            return False
        self.locked[num] = 0
        return True

    def upgrade(self, num: int, user: int) -> bool:
        """
        Interview explanation:
        Same upgrade rules; DFS to unlock descendants after validating ancestors.

        Algorithm:
        - Ancestor walk; DFS collect/clear descendant locks; lock num.

        Complexity: O(n).
        """
        if self.locked[num]:
            return False
        cur = self.parent[num]
        while cur != -1:
            if self.locked[cur]:
                return False
            cur = self.parent[cur]

        saw = False

        def dfs(u: int) -> None:
            nonlocal saw
            for v in self.children[u]:
                if self.locked[v]:
                    saw = True
                    self.locked[v] = 0
                dfs(v)

        dfs(num)
        if not saw:
            return False
        self.locked[num] = user
        return True


# Your LockingTree object will be instantiated and called as such:
# obj = LockingTree(parent)
# param_1 = obj.lock(num,user)
# param_2 = obj.unlock(num,user)
# param_3 = obj.upgrade(num,user)
# @lc code=end

