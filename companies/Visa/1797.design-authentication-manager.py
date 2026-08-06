#
# @lc app=leetcode id=1797 lang=python3
#
# [1797] Design Authentication Manager
#
# https://leetcode.com/problems/design-authentication-manager/description/
#
# algorithms
# Medium (58.66%)
# Likes:    446
# Dislikes: 58
# Total Accepted:    62.4K
# Total Submissions: 106K
# Testcase Example:  "[\"AuthenticationManager\",\"renew\",\"generate\",\"countUnexpiredTokens\",\"generate\",\"renew\",\"renew\",\"countUnexpiredTokens\"]"
#
# There is an authentication system that works with authentication tokens. For
# each session, the user will receive a new authentication token that will
# expire timeToLive seconds after the currentTime. If the token is renewed, the
# expiry time will be extended to expire timeToLive seconds after the
# (potentially different) currentTime.
#
# Implement the AuthenticationManager class:
#
# AuthenticationManager(int timeToLive) constructs the AuthenticationManager
# and sets the timeToLive.
#
# generate(string tokenId, int currentTime) generates a new token with the
# given tokenId at the given currentTime in seconds.
#
# renew(string tokenId, int currentTime) renews the unexpired token with the
# given tokenId at the given currentTime in seconds. If there are no unexpired
# tokens with the given tokenId, the request is ignored, and nothing happens.
#
# countUnexpiredTokens(int currentTime) returns the number of unexpired tokens
# at the given currentTime.
#
# Note that if a token expires at time t, and another action happens on time t
# (renew or countUnexpiredTokens), the expiration takes place before the other
# actions.
#
# Example 1:
#
# Input
# ["AuthenticationManager", "renew", "generate", "countUnexpiredTokens",
# "generate", "renew", "renew", "countUnexpiredTokens"]
# [[5], ["aaa", 1], ["aaa", 2], [6], ["bbb", 7], ["aaa", 8], ["bbb", 10], [15]]
# Output
# [null, null, null, 1, null, null, null, 0]
#
# Explanation
# AuthenticationManager authenticationManager = new AuthenticationManager(5);
# // Constructs the AuthenticationManager with timeToLive = 5 seconds.
# authenticationManager.renew("aaa", 1); // No token exists with tokenId "aaa"
# at time 1, so nothing happens.
# authenticationManager.generate("aaa", 2); // Generates a new token with
# tokenId "aaa" at time 2.
# authenticationManager.countUnexpiredTokens(6); // The token with tokenId
# "aaa" is the only unexpired one at time 6, so return 1.
# authenticationManager.generate("bbb", 7); // Generates a new token with
# tokenId "bbb" at time 7.
# authenticationManager.renew("aaa", 8); // The token with tokenId "aaa"
# expired at time 7, and 8 >= 7, so at time 8 the renew request is ignored, and
# nothing happens.
# authenticationManager.renew("bbb", 10); // The token with tokenId "bbb" is
# unexpired at time 10, so the renew request is fulfilled and now the token
# will expire at time 15.
# authenticationManager.countUnexpiredTokens(15); // The token with tokenId
# "bbb" expires at time 15, and the token with tokenId "aaa" expired at time 7,
# so currently no token is unexpired, so return 0.
#
# Constraints:
#
# 1 <= timeToLive <= 10^8
#
# 1 <= currentTime <= 10^8
#
# 1 <= tokenId.length <= 5
#
# tokenId consists only of lowercase letters.
#
# All calls to generate will contain unique values of tokenId.
#
# The values of currentTime across all the function calls will be strictly
# increasing.
#
# At most 2000 calls will be made to all functions combined.
#

# @lc code=start
class AuthenticationManager:
    def __init__(self, timeToLive: int):
        """
        Interview explanation:
        Design: tokens expire timeToLive seconds after generation/renewal.
        Actions at time t see expirations at t as already expired.

        Algorithm:
        - Store timeToLive; map tokenId → expiry timestamp.

        Complexity: O(1) init.
        """
        self.ttl = timeToLive
        self.expiry = {}

    def generate(self, tokenId: str, currentTime: int) -> None:
        """
        Interview explanation:
        Create/overwrite tokenId to expire at currentTime + timeToLive.

        Algorithm:
        - expiry[tokenId] = currentTime + ttl

        Complexity: O(1).
        """
        self.expiry[tokenId] = currentTime + self.ttl

    def renew(self, tokenId: str, currentTime: int) -> None:
        """
        Interview explanation:
        If token exists and is still unexpired (expiry > currentTime), extend
        expiry to currentTime + ttl; otherwise ignore.

        Algorithm:
        - if token in map and expiry[token] > currentTime: update expiry.

        Complexity: O(1).
        """
        if tokenId in self.expiry and self.expiry[tokenId] > currentTime:
            self.expiry[tokenId] = currentTime + self.ttl

    def countUnexpiredTokens(self, currentTime: int) -> int:
        """
        Interview explanation:
        Count tokens with expiry strictly greater than currentTime.

        Algorithm:
        - sum(1 for e in expiry.values() if e > currentTime)
        - Optional lazy cleanup of expired keys.

        Complexity: O(T) over stored tokens.
        """
        return sum(1 for e in self.expiry.values() if e > currentTime)


class AuthenticationManagerLazyClean:
    """Alternate: lazily delete expired tokens on renew/count."""

    def __init__(self, timeToLive: int):
        """
        Interview explanation:
        Same map of expiries; purge expired entries when counting/renewing.

        Algorithm:
        - ttl + dict token→expiry

        Complexity: O(1) init.
        """
        self.ttl = timeToLive
        self.expiry = {}

    def generate(self, tokenId: str, currentTime: int) -> None:
        """
        Interview explanation:
        Set expiry to currentTime + ttl.

        Algorithm:
        - expiry[tokenId] = currentTime + ttl

        Complexity: O(1).
        """
        self.expiry[tokenId] = currentTime + self.ttl

    def renew(self, tokenId: str, currentTime: int) -> None:
        """
        Interview explanation:
        Renew only if unexpired; drop expired token entry if present.

        Algorithm:
        - if missing or expiry≤currentTime: discard; else extend.

        Complexity: O(1).
        """
        exp = self.expiry.get(tokenId)
        if exp is None or exp <= currentTime:
            self.expiry.pop(tokenId, None)
            return
        self.expiry[tokenId] = currentTime + self.ttl

    def countUnexpiredTokens(self, currentTime: int) -> int:
        """
        Interview explanation:
        Filter map to unexpired tokens, then return size.

        Algorithm:
        - expiry = {k:v for k,v in expiry.items() if v > currentTime}; return len.

        Complexity: O(T).
        """
        self.expiry = {k: v for k, v in self.expiry.items() if v > currentTime}
        return len(self.expiry)


# Your AuthenticationManager object will be instantiated and called as such:
# obj = AuthenticationManager(timeToLive)
# obj.generate(tokenId,currentTime)
# obj.renew(tokenId,currentTime)
# param_3 = obj.countUnexpiredTokens(currentTime)
# @lc code=end
