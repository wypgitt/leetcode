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
    int uniquePaths(int m, int n) {
        /*
        Approach:
        Dynamic programming: ways to reach a cell equals ways from above plus
        ways from the left. A one-row vector is enough because the current cell
        only needs the previous row value dp[c] and current row left dp[c-1].

        Complexity: O(m*n) time and O(n) space.
        */
        vector<int> dp(n, 1);
        for (int r = 1; r < m; ++r) {
            for (int c = 1; c < n; ++c) dp[c] += dp[c - 1];
        }
        return dp.back();
    }
};
