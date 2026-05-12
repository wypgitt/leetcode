#include <algorithm>
#include <array>
#include <climits>
#include <cmath>
#include <condition_variable>
#include <cstdlib>
#include <deque>
#include <functional>
#include <map>
#include <mutex>
#include <numeric>
#include <queue>
#include <set>
#include <sstream>
#include <stack>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

class Solution {
public:
    int longestCommonSubsequence(string text1, string text2) {
        vector<int> dp(text2.size() + 1, 0);

        for (char a : text1) {
            int previousDiagonal = 0;
            for (int j = 1; j <= (int)text2.size(); ++j) {
                int old = dp[j];
                if (a == text2[j - 1]) dp[j] = previousDiagonal + 1;
                else dp[j] = max(dp[j], dp[j - 1]);
                previousDiagonal = old;
            }
        }

        return dp[text2.size()];
    }
};

/*
Interview Explanation

Core idea:
Classic LCS DP. If the current characters match, extend the previous diagonal;
otherwise skip one character from either string.

C++ data structures:
- vector<int> dp compresses the 2D table to one row.
- previousDiagonal stores dp[i-1][j-1] before overwriting.

Algorithm:
For each character in text1, scan text2. Update dp[j] using the LCS recurrence.

Correctness:
For every prefix pair, the optimal LCS either uses the matching last characters
or skips one last character. The update implements exactly these choices, so
the final cell is the LCS length.

Complexity:
O(mn) time and O(n) space.

Edge cases:
- No common characters returns 0.
- Empty strings would return 0.
*/
