#
# @lc app=leetcode id=1268 lang=python3
#
# [1268] Search Suggestions System
#
# https://leetcode.com/problems/search-suggestions-system/description/
#
# algorithms
# Medium (65.22%)
# Likes:    5165
# Dislikes: 267
# Total Accepted:    455K
# Total Submissions: 698K
# Testcase Example:  "[\"mobile\",\"mouse\",\"moneypot\",\"monitor\",\"mousepad\"]"
#
# You are given an array of strings products and a string searchWord.
#
# Design a system that suggests at most three product names from products after
# each character of searchWord is typed. Suggested products should have common
# prefix with searchWord. If there are more than three products with a common
# prefix return the three lexicographically minimums products.
#
# Return a list of lists of the suggested products after each character of
# searchWord is typed.
#
# Example 1:
#
# Input: products = ["mobile","mouse","moneypot","monitor","mousepad"],
# searchWord = "mouse"
# Output:
# [["mobile","moneypot","monitor"],["mobile","moneypot","monitor"],["mouse","mousepad"],["mouse","mousepad"],["mouse","mousepad"]]
# Explanation: products sorted lexicographically =
# ["mobile","moneypot","monitor","mouse","mousepad"].
# After typing m and mo all products match and we show user
# ["mobile","moneypot","monitor"].
# After typing mou, mous and mouse the system suggests ["mouse","mousepad"].
#
# Example 2:
#
# Input: products = ["havana"], searchWord = "havana"
# Output: [["havana"],["havana"],["havana"],["havana"],["havana"],["havana"]]
# Explanation: The only word "havana" will be always suggested while typing the
# search word.
#
# Constraints:
#
# 1 <= products.length <= 1000
#
# 1 <= products[i].length <= 3000
#
# 1 <= sum(products[i].length) <= 2 * 10^4
#
# All the strings of products are unique.
#
# products[i] consists of lowercase English letters.
#
# 1 <= searchWord.length <= 1000
#
# searchWord consists of lowercase English letters.
#

# @lc code=start

from typing import List


class Solution:
    def suggestedProducts(
        self, products: List[str], searchWord: str
    ) -> List[List[str]]:
        """
        Interview explanation:
        After sorting products, for each prefix of searchWord binary-search
        the first product >= prefix and take up to 3 that start with prefix.

        Algorithm:
        - products.sort().
        - For i=1..len(searchWord): prefix=searchWord[:i]; bisect_left;
          collect up to 3 matching startswith.

        Complexity: O(n log n * L + m log n * L) with n products, m=|search|.
        """
        import bisect

        products.sort()
        ans = []
        prefix = ""
        for ch in searchWord:
            prefix += ch
            i = bisect.bisect_left(products, prefix)
            sug = []
            for j in range(i, min(i + 3, len(products))):
                if products[j].startswith(prefix):
                    sug.append(products[j])
            ans.append(sug)
        return ans

    def suggestedProducts_trie(
        self, products: List[str], searchWord: str
    ) -> List[List[str]]:
        """
        Interview explanation:
        Alternate Trie: insert all products; along searchWord walk, each node
        stores up to 3 suggestions.

        Algorithm:
        - Build trie with sorted products storing top-3 at each node.
        - Walk searchWord; append node.suggestions or [].

        Complexity: O(total chars) build/query.
        """
        products.sort()

        class Node:
            def __init__(self):
                self.child = {}
                self.sug: List[str] = []

        root = Node()
        for w in products:
            cur = root
            for ch in w:
                if ch not in cur.child:
                    cur.child[ch] = Node()
                cur = cur.child[ch]
                if len(cur.sug) < 3:
                    cur.sug.append(w)
        ans = []
        cur = root
        for ch in searchWord:
            if cur and ch in cur.child:
                cur = cur.child[ch]
                ans.append(cur.sug[:])
            else:
                cur = None
                ans.append([])
        return ans
# @lc code=end
