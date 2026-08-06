#
# @lc app=leetcode id=1600 lang=python3
#
# [1600] Throne Inheritance
#
# https://leetcode.com/problems/throne-inheritance/description/
#
# algorithms
# Medium (67.71%)
# Likes:    321
# Dislikes: 341
# Total Accepted:    30.9K
# Total Submissions: 45.7K
# Testcase Example:  "[\"ThroneInheritance\",\"birth\",\"birth\",\"birth\",\"birth\",\"birth\",\"birth\",\"getInheritanceOrder\",\"death\",\"getInheritanceOrder\"]"
#
# A kingdom consists of a king, his children, his grandchildren, and so on.
# Every once in a while, someone in the family dies or a child is born.
#
# The kingdom has a well-defined order of inheritance that consists of the king
# as the first member. Let's define the recursive function Successor(x,
# curOrder), which given a person x and the inheritance order so far, returns
# who should be the next person after x in the order of inheritance.
#
# Successor(x, curOrder):
# if x has no children or all of x's children are in curOrder:
# if x is the king return null
# else return Successor(x's parent, curOrder)
# else return x's oldest child who's not in curOrder
#
# For example, assume we have a kingdom that consists of the king, his children
# Alice and Bob (Alice is older than Bob), and finally Alice's son Jack.
#
# In the beginning, curOrder will be ["king"].
#
# Calling Successor(king, curOrder) will return Alice, so we append to curOrder
# to get ["king", "Alice"].
#
# Calling Successor(Alice, curOrder) will return Jack, so we append to curOrder
# to get ["king", "Alice", "Jack"].
#
# Calling Successor(Jack, curOrder) will return Bob, so we append to curOrder
# to get ["king", "Alice", "Jack", "Bob"].
#
# Calling Successor(Bob, curOrder) will return null. Thus the order of
# inheritance will be ["king", "Alice", "Jack", "Bob"].
#
# Using the above function, we can always obtain a unique order of inheritance.
#
# Implement the ThroneInheritance class:
#
# ThroneInheritance(string kingName) Initializes an object of the
# ThroneInheritance class. The name of the king is given as part of the
# constructor.
#
# void birth(string parentName, string childName) Indicates that parentName
# gave birth to childName.
#
# void death(string name) Indicates the death of name. The death of the person
# doesn't affect the Successor function nor the current inheritance order. You
# can treat it as just marking the person as dead.
#
# string[] getInheritanceOrder() Returns a list representing the current order
# of inheritance excluding dead people.
#
# Example 1:
#
# Input
# ["ThroneInheritance", "birth", "birth", "birth", "birth", "birth", "birth",
# "getInheritanceOrder", "death", "getInheritanceOrder"]
# [["king"], ["king", "andy"], ["king", "bob"], ["king", "catherine"], ["andy",
# "matthew"], ["bob", "alex"], ["bob", "asha"], [null], ["bob"], [null]]
# Output
# [null, null, null, null, null, null, null, ["king", "andy", "matthew", "bob",
# "alex", "asha", "catherine"], null, ["king", "andy", "matthew", "alex",
# "asha", "catherine"]]
#
# Explanation
# ThroneInheritance t= new ThroneInheritance("king"); // order: king
# t.birth("king", "andy"); // order: king > andy
# t.birth("king", "bob"); // order: king > andy > bob
# t.birth("king", "catherine"); // order: king > andy > bob > catherine
# t.birth("andy", "matthew"); // order: king > andy > matthew > bob > catherine
# t.birth("bob", "alex"); // order: king > andy > matthew > bob > alex >
# catherine
# t.birth("bob", "asha"); // order: king > andy > matthew > bob > alex > asha >
# catherine
# t.getInheritanceOrder(); // return ["king", "andy", "matthew", "bob", "alex",
# "asha", "catherine"]
# t.death("bob"); // order: king > andy > matthew > bob > alex > asha >
# catherine
# t.getInheritanceOrder(); // return ["king", "andy", "matthew", "alex",
# "asha", "catherine"]
#
# Constraints:
#
# 1 <= kingName.length, parentName.length, childName.length, name.length <= 15
#
# kingName, parentName, childName, and name consist of lowercase English
# letters only.
#
# All arguments childName and kingName are distinct.
#
# All name arguments of death will be passed to either the constructor or as
# childName to birth first.
#
# For each call to birth(parentName, childName), it is guaranteed that
# parentName is alive.
#
# At most 10^5 calls will be made to birth and death.
#
# At most 10 calls will be made to getInheritanceOrder.
#

# @lc code=start
from typing import List
from collections import defaultdict


class ThroneInheritance:
    def __init__(self, kingName: str):
        """
        Interview explanation:
        Mantain a royal family tree; inheritance order is preorder DFS of
        living people (skip dead). birth appends child; death marks deceased.

        Algorithm:
        - children: name → list of children in birth order; dead set; king root.

        Complexity: O(1) init.
        """
        self.king = kingName
        self.children = defaultdict(list)
        self.dead = set()

    def birth(self, parentName: str, childName: str) -> None:
        """
        Interview explanation:
        Record child under parent in birth order for successor DFS.

        Algorithm:
        - children[parent].append(child)

        Complexity: O(1).
        """
        self.children[parentName].append(childName)

    def death(self, name: str) -> None:
        """
        Interview explanation:
        Mark person dead; still in tree for lineage but omitted from order.

        Algorithm:
        - dead.add(name)

        Complexity: O(1).
        """
        self.dead.add(name)

    def getInheritanceOrder(self) -> List[str]:
        """
        Interview explanation:
        Current inheritance: DFS preorder from king; include node if alive,
        then recurse children in birth order.

        Algorithm:
        - dfs(x): if x not dead append; for c in children[x]: dfs(c)

        Complexity: O(n) time/space per query.
        """
        order: List[str] = []

        def dfs(name: str) -> None:
            if name not in self.dead:
                order.append(name)
            for child in self.children[name]:
                dfs(child)

        dfs(self.king)
        return order


# Your ThroneInheritance object will be instantiated and called as such:
# obj = ThroneInheritance(kingName)
# obj.birth(parentName,childName)
# obj.death(name)
# param_3 = obj.getInheritanceOrder()
# @lc code=end

