#
# @lc app=leetcode id=1472 lang=python3
#
# [1472] Design Browser History
#
# https://leetcode.com/problems/design-browser-history/description/
#
# algorithms
# Medium (78.42%)
# Likes:    4181
# Dislikes: 271
# Total Accepted:    357K
# Total Submissions: 455K
# Testcase Example:  "[\"BrowserHistory\",\"visit\",\"visit\",\"visit\",\"back\",\"back\",\"forward\",\"visit\",\"forward\",\"back\",\"back\"]"
#
# You have a browser of one tab where you start on the homepage and you can
# visit another url, get back in the history number of steps or move forward in
# the history number of steps.
#
# Implement the BrowserHistory class:
#
# BrowserHistory(string homepage) Initializes the object with the homepage of
# the browser.
#
# void visit(string url) Visits url from the current page. It clears up all the
# forward history.
#
# string back(int steps) Move steps back in history. If you can only return x
# steps in the history and steps > x, you will return only x steps. Return the
# current url after moving back in history at most steps.
#
# string forward(int steps) Move steps forward in history. If you can only
# forward x steps in the history and steps > x, you will forward only x steps.
# Return the current url after forwarding in history at most steps.
#
# Example:
#
# Input:
# ["BrowserHistory","visit","visit","visit","back","back","forward","visit","forward","back","back"]
# [["leetcode.com"],["google.com"],["facebook.com"],["youtube.com"],[1],[1],[1],["linkedin.com"],[2],[2],[7]]
# Output:
# [null,null,null,null,"facebook.com","google.com","facebook.com",null,"linkedin.com","google.com","leetcode.com"]
#
# Explanation:
# BrowserHistory browserHistory = new BrowserHistory("leetcode.com");
# browserHistory.visit("google.com"); // You are in "leetcode.com". Visit
# "google.com"
# browserHistory.visit("facebook.com"); // You are in "google.com". Visit
# "facebook.com"
# browserHistory.visit("youtube.com"); // You are in "facebook.com". Visit
# "youtube.com"
# browserHistory.back(1); // You are in "youtube.com", move back to
# "facebook.com" return "facebook.com"
# browserHistory.back(1); // You are in "facebook.com", move back to
# "google.com" return "google.com"
# browserHistory.forward(1); // You are in "google.com", move forward to
# "facebook.com" return "facebook.com"
# browserHistory.visit("linkedin.com"); // You are in "facebook.com". Visit
# "linkedin.com"
# browserHistory.forward(2); // You are in "linkedin.com", you cannot move
# forward any steps.
# browserHistory.back(2); // You are in "linkedin.com", move back two steps to
# "facebook.com" then to "google.com". return "google.com"
# browserHistory.back(7); // You are in "google.com", you can move back only
# one step to "leetcode.com". return "leetcode.com"
#
# Constraints:
#
# 1 <= homepage.length <= 20
#
# 1 <= url.length <= 20
#
# 1 <= steps <= 100
#
# homepage and url consist of '.' or lower case English letters.
#
# At most 5000 calls will be made to visit, back, and forward.
#

# @lc code=start
class BrowserHistory:
    def __init__(self, homepage: str):
        """
        Interview explanation:
        One-tab browser history: visit clears forward; back/forward move by
        steps. Store history list + current index.

        Algorithm:
        - self.hist = [homepage]; self.i = 0

        Complexity: O(1) init.
        """
        self.hist = [homepage]
        self.i = 0

    def visit(self, url: str) -> None:
        """
        Interview explanation:
        Visit url from current page; discard all forward history.

        Algorithm:
        - Truncate hist to i+1; append url; i = len-1.

        Complexity: O(1) amortized (truncate is O(forward length)).
        """
        self.hist = self.hist[: self.i + 1]
        self.hist.append(url)
        self.i += 1

    def back(self, steps: int) -> str:
        """
        Interview explanation:
        Move back up to steps pages; return current url.

        Algorithm:
        - i = max(0, i-steps); return hist[i]

        Complexity: O(1).
        """
        self.i = max(0, self.i - steps)
        return self.hist[self.i]

    def forward(self, steps: int) -> str:
        """
        Interview explanation:
        Move forward up to steps pages; return current url.

        Algorithm:
        - i = min(len-1, i+steps); return hist[i]

        Complexity: O(1).
        """
        self.i = min(len(self.hist) - 1, self.i + steps)
        return self.hist[self.i]


class BrowserHistoryTwoStacks:
    def __init__(self, homepage: str):
        """
        Interview explanation:
        Alternate: back stack (past including current) + forward stack.
        visit clears forward; back/forward pop/push between stacks.

        Algorithm:
        - back=[homepage]; forward=[]

        Complexity: O(1) init.
        """
        self.back = [homepage]
        self.fwd = []

    def visit(self, url: str) -> None:
        """
        Interview explanation:
        Push url onto back; clear forward stack.

        Algorithm:
        - back.append(url); forward.clear()

        Complexity: O(1) (+ clear forward length).
        """
        self.back.append(url)
        self.fwd.clear()

    def back(self, steps: int) -> str:
        """
        Interview explanation:
        Pop from back onto forward, keeping at least homepage.

        Algorithm:
        - While steps and len(back)>1: fwd.append(back.pop()); steps-=1.

        Complexity: O(steps).
        """
        while steps and len(self.back) > 1:
            self.fwd.append(self.back.pop())
            steps -= 1
        return self.back[-1]

    def forward(self, steps: int) -> str:
        """
        Interview explanation:
        Pop from forward onto back up to steps.

        Algorithm:
        - While steps and fwd: back.append(fwd.pop()); steps-=1.

        Complexity: O(steps).
        """
        while steps and self.fwd:
            self.back.append(self.fwd.pop())
            steps -= 1
        return self.back[-1]


# Your BrowserHistory object will be instantiated and called as such:
# obj = BrowserHistory(homepage)
# obj.visit(url)
# param_2 = obj.back(steps)
# param_3 = obj.forward(steps)
# @lc code=end
