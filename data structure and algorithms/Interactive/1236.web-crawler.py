#
# @lc app=leetcode id=1236 lang=python3
#
# [1236] Web Crawler
#
# https://leetcode.com/problems/web-crawler/description/
#
# algorithms
# Medium (68.72%)
# Likes:    310
# Dislikes: 339
# Total Accepted:    58.2K
# Total Submissions: 84.7K
# Testcase Example:  "[\"http://news.yahoo.com\",\"http://news.yahoo.com/news\",\"http://news.yahoo.com/news/topics/\",\"http://news.google.com\",\"http://news.yahoo.com/us\"]\n[[2,0],[2,1],[3,2],[3,1],[0,4]]\n\"http://news.yahoo.com/news/topics/\""
#
#
# Given a url startUrl and an interface HtmlParser, implement a web
# crawler to crawl all links that are under the same hostname as startUrl.
#
# Return all urls obtained by your web crawler in any order.
#
# Your crawler should:
#
# Start from the page: startUrl
#
# Call HtmlParser.getUrls(url) to get all urls from a webpage of given
# url.
#
# Do not crawl the same link twice.
#
# Explore only the links that are under the same hostname as startUrl.
#
# As shown in the example url above, the hostname is example.org. For
# simplicity sake, you may assume all urls use http protocol without any
# port specified. For example, the urls http://leetcode.com/problems and
# http://leetcode.com/contest are under the same hostname, while urls
# http://example.org/test and http://example.com/abc are not under the
# same hostname.
#
# The HtmlParser interface is defined as such:
#
# interface HtmlParser {
#   // Return a list of all urls from a webpage of given url.
#   public List<String> getUrls(String url);
# }
#
# Below are two examples explaining the functionality of the problem, for
# custom testing purposes you'll have three variables urls, edges and
# startUrl. Notice that you will only have access to startUrl in your
# code, while urls and edges are not directly accessible to you in code.
#
# Note: Consider the same URL with the trailing slash "/" as a different
# URL. For example, "http://news.yahoo.com", and "http://news.yahoo.com/"
# are different urls.
#
# Example 1:
#
# Input:
# urls = [
#   "http://news.yahoo.com",
#   "http://news.yahoo.com/news",
#   "http://news.yahoo.com/news/topics/",
#   "http://news.google.com",
#   "http://news.yahoo.com/us"
# ]
# edges = [[2,0],[2,1],[3,2],[3,1],[0,4]]
# startUrl = "http://news.yahoo.com/news/topics/"
# Output: [
#   "http://news.yahoo.com",
#   "http://news.yahoo.com/news",
#   "http://news.yahoo.com/news/topics/",
#   "http://news.yahoo.com/us"
# ]
#
# Example 2:
#
# Input:
# urls = [
#   "http://news.yahoo.com",
#   "http://news.yahoo.com/news",
#   "http://news.yahoo.com/news/topics/",
#   "http://news.google.com"
# ]
# edges = [[0,2],[2,1],[3,2],[3,1],[3,0]]
# startUrl = "http://news.google.com"
# Output: ["http://news.google.com"]
# Explanation: The startUrl links to all other pages that do not share the
# same hostname.
#
# Constraints:
#
# 1 <= urls.length <= 1000
#
# 1 <= urls[i].length <= 300
#
# startUrl is one of the urls.
#
# Hostname label must be from 1 to 63 characters long, including the dots,
# may contain only the ASCII letters from 'a' to 'z', digits  from '0' to
# '9' and the hyphen-minus character ('-').
#
# The hostname may not start or end with the hyphen-minus character ('-').
#
# See:
# https://en.wikipedia.org/wiki/Hostname#Restrictions_on_valid_hostnames
#
# You may assume there're no duplicates in url library.
#
# @lc code=start
from typing import List
from collections import deque

try:
    HtmlParser
except NameError:
    class HtmlParser:
        def getUrls(self, url: str) -> List[str]:
            return []

class Solution:
    def crawl(self, startUrl: str, htmlParser: 'HtmlParser') -> List[str]:
        """
        Interview explanation:
        Premium web crawler. Start from startUrl; BFS/DFS only follow URLs with
        the same hostname. Use HtmlParser.getUrls.

        Algorithm:
        - Extract hostname from startUrl; BFS queue; visited set; add same-host urls

        Complexity: O(V+E) pages/links.
        """
        def host(url: str) -> str:
            # http://hostname/...
            return url.split("/")[2]

        start_host = host(startUrl)
        seen = {startUrl}
        q = deque([startUrl])
        while q:
            cur = q.popleft()
            for nxt in htmlParser.getUrls(cur):
                if nxt not in seen and host(nxt) == start_host:
                    seen.add(nxt)
                    q.append(nxt)
        return list(seen)

    def crawl_dfs(self, startUrl: str, htmlParser: 'HtmlParser') -> List[str]:
        """
        Interview explanation:
        Alternate DFS recursion with visited set, same hostname filter.

        Algorithm:
        - dfs(url): mark; for same-host unvisited neighbors recurse

        Complexity: O(V+E).
        """
        def host(url: str) -> str:
            return url.split("/")[2]

        start_host = host(startUrl)
        seen = set()

        def dfs(url: str) -> None:
            seen.add(url)
            for nxt in htmlParser.getUrls(url):
                if nxt not in seen and host(nxt) == start_host:
                    dfs(nxt)

        dfs(startUrl)
        return list(seen)
# @lc code=end
