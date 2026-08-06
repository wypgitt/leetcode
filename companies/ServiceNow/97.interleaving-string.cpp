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
    bool isInterleave(string s1, string s2, string s3) {
        /*
        Approach:
        dp[j] means whether s3[0:i+j] can be formed from s1[0:i] and s2[0:j]
        for the current i. The last character can come from s1 or s2 if that
        previous state was valid and the character matches.

        Complexity: O(m*n) time and O(n) space.
        */
        if (s1.size() + s2.size() != s3.size()) return false;
        int m = (int)s1.size(), n = (int)s2.size();
        vector<bool> dp(n + 1, false);
        dp[0] = true;
        for (int i = 0; i <= m; ++i) {
            for (int j = 0; j <= n; ++j) {
                if (i == 0 && j == 0) continue;
                int k = i + j - 1;
                bool fromS1 = i > 0 && dp[j] && s1[i - 1] == s3[k];
                bool fromS2 = j > 0 && dp[j - 1] && s2[j - 1] == s3[k];
                dp[j] = fromS1 || fromS2;
            }
        }
        return dp[n];
    }
};
