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
    int minDistance(string word1, string word2) {
        /*
        Approach:
        dp[j] is the edit distance from the processed prefix of word1 to
        word2[0:j]. For each character of word1, update the row using delete,
        insert, and replace/match transitions while carrying the diagonal value.

        Complexity: O(m*n) time and O(n) space.
        */
        int m = (int)word1.size(), n = (int)word2.size();
        vector<int> dp(n + 1);
        iota(dp.begin(), dp.end(), 0);
        for (int i = 1; i <= m; ++i) {
            int prevDiag = dp[0];
            dp[0] = i;
            for (int j = 1; j <= n; ++j) {
                int old = dp[j];
                if (word1[i - 1] == word2[j - 1]) dp[j] = prevDiag;
                else dp[j] = 1 + min({dp[j], dp[j - 1], prevDiag});
                prevDiag = old;
            }
        }
        return dp[n];
    }
};
