#
# @lc app=leetcode id=1236 lang=python3
#
# [1236] Web Crawler
#
# https://leetcode.com/problems/web-crawler/description/
#
# algorithms
# Medium (68.83%)
# Likes:    309
# Dislikes: 338
# Total Accepted:    56.1K
# Total Submissions: 81.5K
# Testcase Example:  '["http://news.yahoo.com","http://news.yahoo.com/news","http://news.yahoo.com/news/topics/","http://news.google.com","http://news.yahoo.com/us"]\n' +
# '[[2,0],[2,1],[3,2],[3,1],[0,4]]\n' +
# '"http://news.yahoo.com/news/topics/"'
#
# Given a url startUrl and an interface HtmlParser, implement a web crawler to
# crawl all links that are under the same hostname as startUrl. 
# 
# Return all urls obtained by your web crawler in any order.
# 
# Your crawler should:
# 
# 
# Start from the page: startUrl
# Call HtmlParser.getUrls(url) to get all urls from a webpage of given url.
# Do not crawl the same link twice.
# Explore only the links that are under the same hostname as startUrl.
# 
# 
# 
# 
# As shown in the example url above, the hostname is example.org. For
# simplicity sake, you may assume all urls use http protocol without any port
# specified. For example, the urls http://leetcode.com/problems and
# http://leetcode.com/contest are under the same hostname, while urls
# http://example.org/test and http://example.com/abc are not under the same
# hostname.
# 
# The HtmlParser interface is defined as such: 
# 
# 
# interface HtmlParser {
# ⁠ // Return a list of all urls from a webpage of given url.
# ⁠ public List<String> getUrls(String url);
# }
# 
# Below are two examples explaining the functionality of the problem, for
# custom testing purposes you'll have three variables urls, edges and startUrl.
# Notice that you will only have access to startUrl in your code, while urls
# and edges are not directly accessible to you in code.
# 
# Note: Consider the same URL with the trailing slash "/" as a different URL.
# For example, "http://news.yahoo.com", and "http://news.yahoo.com/" are
# different urls.
# 
# 
# Example 1:
# 
# 
# 
# 
# Input:
# urls = [
# "http://news.yahoo.com",
# "http://news.yahoo.com/news",
# "http://news.yahoo.com/news/topics/",
# "http://news.google.com",
# "http://news.yahoo.com/us"
# ]
# edges = [[2,0],[2,1],[3,2],[3,1],[0,4]]
# startUrl = "http://news.yahoo.com/news/topics/"
# Output: [
# "http://news.yahoo.com",
# "http://news.yahoo.com/news",
# "http://news.yahoo.com/news/topics/",
# "http://news.yahoo.com/us"
# ]
# 
# 
# Example 2:
# 
# 
# 
# 
# Input: 
# urls = [
# "http://news.yahoo.com",
# "http://news.yahoo.com/news",
# "http://news.yahoo.com/news/topics/",
# "http://news.google.com"
# ]
# edges = [[0,2],[2,1],[3,2],[3,1],[3,0]]
# startUrl = "http://news.google.com"
# Output: ["http://news.google.com"]
# Explanation: The startUrl links to all other pages that do not share the same
# hostname.
# 
# 
# Constraints:
# 
# 
# 1 <= urls.length <= 1000
# 1 <= urls[i].length <= 300
# startUrl is one of the urls.
# Hostname label must be from 1 to 63 characters long, including the dots, may
# contain only the ASCII letters from 'a' to 'z', digits  from '0' to '9' and
# the hyphen-minus character ('-').
# The hostname may not start or end with the hyphen-minus character ('-'). 
# See:
# https://en.wikipedia.org/wiki/Hostname#Restrictions_on_valid_hostnames
# You may assume there're no duplicates in url library.
# 
# 
#

# @lc code=start
from collections import deque
from typing import List
from urllib.parse import urlparse


# """
# This is HtmlParser's API interface.
# You should not implement it, or speculate about its implementation
# """
#class HtmlParser(object):
#    def getUrls(self, url):
#        """
#        :type url: str
#        :rtype List[str]
#        """

class Solution:
    def crawl(self, startUrl: str, htmlParser: 'HtmlParser') -> List[str]:
        hostname = urlparse(startUrl).netloc
        seen = {startUrl}
        queue = deque([startUrl])

        while queue:
            url = queue.popleft()
            for next_url in htmlParser.getUrls(url):
                if next_url not in seen and urlparse(next_url).netloc == hostname:
                    seen.add(next_url)
                    queue.append(next_url)

        return list(seen)
# @lc code=end

# Explanation
# -----------
# Parse the hostname of startUrl, then perform BFS. For each visited URL, ask
# HtmlParser for outgoing URLs and enqueue only unseen URLs with the same
# hostname.
#
# The queue is used because crawling is a graph traversal. The seen set is
# essential to prevent cycles and duplicate parser calls.
#
# Host filtering uses urlparse(...).netloc so paths under the same host are
# included while different domains are skipped. The problem treats trailing
# slashes as different URLs, and the seen set preserves that distinction.
#
# Edge cases: start URL with no outgoing links; links that point back to
# already visited pages; same path text on another hostname.
#
# Time complexity: O(V + E) parser edges reachable on the same host.
# Space complexity: O(V) for queue and seen set.
