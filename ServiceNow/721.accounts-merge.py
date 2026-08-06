#
# @lc app=leetcode id=721 lang=python3
#
# [721] Accounts Merge
#
# https://leetcode.com/problems/accounts-merge/description/
#
# algorithms
# Medium (61.82%)
# Likes:    7817
# Dislikes: 1329
# Total Accepted:    660K
# Total Submissions: 1.1M
# Testcase Example:  "[[\"John\",\"johnsmith@mail.com\",\"john_newyork@mail.com\"],[\"John\",\"johnsmith@mail.com\",\"john00@mail.com\"],[\"Mary\",\"mary@mail.com\"],[\"John\",\"johnnybravo@mail.com\"]]"
#
# Given a list of accounts where each element accounts[i] is a list of strings,
# where the first element accounts[i][0] is a name, and the rest of the
# elements are emails representing emails of the account.
#
# Now, we would like to merge these accounts. Two accounts definitely belong to
# the same person if there is some common email to both accounts. Note that
# even if two accounts have the same name, they may belong to different people
# as people could have the same name. A person can have any number of accounts
# initially, but all of their accounts definitely have the same name.
#
# After merging the accounts, return the accounts in the following format: the
# first element of each account is the name, and the rest of the elements are
# emails in sorted order. The accounts themselves can be returned in any order.
#
# Example 1:
#
# Input: accounts =
# [["John","johnsmith@mail.com","john_newyork@mail.com"],["John","johnsmith@mail.com","john00@mail.com"],["Mary","mary@mail.com"],["John","johnnybravo@mail.com"]]
# Output:
# [["John","john00@mail.com","john_newyork@mail.com","johnsmith@mail.com"],["Mary","mary@mail.com"],["John","johnnybravo@mail.com"]]
# Explanation:
# The first and second John's are the same person as they have the common email
# "johnsmith@mail.com".
# The third John and Mary are different people as none of their email addresses
# are used by other accounts.
# We could return these lists in any order, for example the answer [['Mary',
# 'mary@mail.com'], ['John', 'johnnybravo@mail.com'],
# ['John', 'john00@mail.com', 'john_newyork@mail.com', 'johnsmith@mail.com']]
# would still be accepted.
#
# Example 2:
#
# Input: accounts =
# [["Gabe","Gabe0@m.co","Gabe3@m.co","Gabe1@m.co"],["Kevin","Kevin3@m.co","Kevin5@m.co","Kevin0@m.co"],["Ethan","Ethan5@m.co","Ethan4@m.co","Ethan0@m.co"],["Hanzo","Hanzo3@m.co","Hanzo1@m.co","Hanzo0@m.co"],["Fern","Fern5@m.co","Fern1@m.co","Fern0@m.co"]]
# Output:
# [["Ethan","Ethan0@m.co","Ethan4@m.co","Ethan5@m.co"],["Gabe","Gabe0@m.co","Gabe1@m.co","Gabe3@m.co"],["Hanzo","Hanzo0@m.co","Hanzo1@m.co","Hanzo3@m.co"],["Kevin","Kevin0@m.co","Kevin3@m.co","Kevin5@m.co"],["Fern","Fern0@m.co","Fern1@m.co","Fern5@m.co"]]
#
# Constraints:
#
# 1 <= accounts.length <= 1000
#
# 2 <= accounts[i].length <= 10
#
# 1 <= accounts[i][j].length <= 30
#
# accounts[i][0] consists of English letters.
#
# accounts[i][j] (for j > 0) is a valid email.
#


# @lc code=start
from collections import defaultdict
from typing import Dict, List, Set


class Solution:
    def accountsMerge(self, accounts: List[List[str]]) -> List[List[str]]:
        """
        Interview explanation:
        Emails are nodes; shared emails imply the same person. Union-Find merges
        emails that co-occur in an account; then group emails by root and attach
        the owner name, sorting emails in each group.

        Algorithm:
        - Map each email to a parent (UF). For each account, union all its emails
          to the first email; record email -> name.
        - Bucket emails by find(root); build [name] + sorted emails.

        Complexity: O(A * α(E) + E log E) time where A is total email occurrences
        and E unique emails; O(E) space.
        """
        parent: Dict[str, str] = {}
        email_name: Dict[str, str] = {}

        def find(x: str) -> str:
            parent.setdefault(x, x)
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: str, b: str) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        for acc in accounts:
            name = acc[0]
            first = acc[1]
            for email in acc[1:]:
                email_name[email] = name
                union(first, email)

        groups: Dict[str, List[str]] = defaultdict(list)
        for email in email_name:
            groups[find(email)].append(email)

        return [[email_name[root]] + sorted(emails) for root, emails in groups.items()]

    def accountsMerge_dfs(self, accounts: List[List[str]]) -> List[List[str]]:
        """
        Interview explanation:
        Alternate classic: build an undirected graph of emails (edges between
        emails in the same account), DFS/BFS each component, attach the name.

        Algorithm:
        - Graph: connect consecutive emails in each account; map email -> name.
        - For each unvisited email, DFS collect component; emit sorted list.

        Complexity: O(A + E log E) time, O(E + A) space.
        """
        graph: Dict[str, Set[str]] = defaultdict(set)
        email_name: Dict[str, str] = {}
        for acc in accounts:
            name = acc[0]
            for email in acc[1:]:
                email_name[email] = name
            for i in range(1, len(acc) - 1):
                graph[acc[i]].add(acc[i + 1])
                graph[acc[i + 1]].add(acc[i])
            graph.setdefault(acc[1], set())

        seen: Set[str] = set()
        ans: List[List[str]] = []

        def dfs(email: str, bucket: List[str]) -> None:
            seen.add(email)
            bucket.append(email)
            for nei in graph[email]:
                if nei not in seen:
                    dfs(nei, bucket)

        for email in email_name:
            if email not in seen:
                bucket: List[str] = []
                dfs(email, bucket)
                ans.append([email_name[email]] + sorted(bucket))
        return ans
# @lc code=end

