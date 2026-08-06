#include <algorithm>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
using namespace std;


class Solution {
public:
    int numDecodings(string s) {
        /*
        Approach:
        dp[i] depends only on dp[i-1] for a valid one-digit decode and dp[i-2]
        for a valid two-digit decode from 10 to 26. Keep those two previous
        counts instead of the full DP table.

        Complexity: O(n) time and O(1) space.
        */
        if (s.empty() || s[0] == '0') return 0;
        int twoBack = 1, oneBack = 1;
        for (int i = 1; i < (int)s.size(); ++i) {
            int cur = 0;
            if (s[i] != '0') cur += oneBack;
            int twoDigit = (s[i - 1] - '0') * 10 + (s[i] - '0');
            if (10 <= twoDigit && twoDigit <= 26) cur += twoBack;
            twoBack = oneBack;
            oneBack = cur;
        }
        return oneBack;
    }
};
