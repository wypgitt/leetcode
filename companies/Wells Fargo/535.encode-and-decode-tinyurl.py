#
# @lc app=leetcode id=535 lang=python3
#
# [535] Encode and Decode TinyURL
#
# https://leetcode.com/problems/encode-and-decode-tinyurl/description/
#
# algorithms
# Medium (86.65%)
# Likes:    2151
# Dislikes: 3822
# Total Accepted:    317K
# Total Submissions: 366K
# Testcase Example:  "\"https://leetcode.com/problems/design-tinyurl\""
#
# Note: This is a companion problem to the System Design problem: Design
# TinyURL.
#
# TinyURL is a URL shortening service where you enter a URL such as
# https://leetcode.com/problems/design-tinyurl and it returns a short URL such
# as http://tinyurl.com/4e9iAk. Design a class to encode a URL and decode a
# tiny URL.
#
# There is no restriction on how your encode/decode algorithm should work. You
# just need to ensure that a URL can be encoded to a tiny URL and the tiny URL
# can be decoded to the original URL.
#
# Implement the Solution class:
#
# Solution() Initializes the object of the system.
#
# String encode(String longUrl) Returns a tiny URL for the given longUrl.
#
# String decode(String shortUrl) Returns the original long URL for the given
# shortUrl. It is guaranteed that the given shortUrl was encoded by the same
# object.
#
# Example 1:
#
# Input: url = "https://leetcode.com/problems/design-tinyurl"
# Output: "https://leetcode.com/problems/design-tinyurl"
#
# Explanation:
# Solution obj = new Solution();
# string tiny = obj.encode(url); // returns the encoded tiny url.
# string ans = obj.decode(tiny); // returns the original url after decoding it.
#
# Constraints:
#
# 1 <= url.length <= 10^4
#
# url is guranteed to be a valid URL.
#

# @lc code=start
class Codec:
    def __init__(self):
        """
        Interview explanation:
        TinyURL needs bidirectional O(1) lookup between long URLs and short
        codes. An incrementing counter yields unique short keys without
        hashing collisions.

        Algorithm:
        - long_to_short / short_to_long maps.
        - counter assigns the next numeric code.

        Complexity: O(1) setup; O(n) space for n encoded URLs.
        """
        self.long_to_short = {}
        self.short_to_long = {}
        self.counter = 0

    def encode(self, longUrl: str) -> str:
        """
        Interview explanation:
        Map each new long URL to a unique short code (incrementing counter).
        Store bidirectional maps so decode is O(1).

        Algorithm:
        - If already encoded, reuse short URL.
        - Else assign next counter as code under a fixed prefix.

        Complexity: O(1) amortized per encode (string copy of URL).
        """
        if longUrl in self.long_to_short:
            return self.long_to_short[longUrl]
        short = "http://tinyurl.com/" + str(self.counter)
        self.counter += 1
        self.long_to_short[longUrl] = short
        self.short_to_long[short] = longUrl
        return short

    def decode(self, shortUrl: str) -> str:
        """
        Interview explanation:
        Look up the short URL in the reverse map built during encode.

        Algorithm:
        - Return short_to_long[shortUrl].

        Complexity: O(1).
        """
        return self.short_to_long[shortUrl]


# Your Codec object will be instantiated and called as such:
# codec = Codec()
# codec.decode(codec.encode(url))
# @lc code=end

