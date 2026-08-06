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
    int numTrees(int n) {
        /*
        Approach:
        Catalan DP. Choosing a root splits the remaining nodes into independent
        left and right subtree sizes. Sum dp[left] * dp[right] over all possible
        left subtree sizes.

        Complexity: O(n^2) time and O(n) space.
        */
        vector<int> dp(n + 1, 0);
        dp[0] = 1;
        if (n >= 1) dp[1] = 1;
        for (int nodes = 2; nodes <= n; ++nodes) {
            for (int left = 0; left < nodes; ++left) dp[nodes] += dp[left] * dp[nodes - 1 - left];
        }
        return dp[n];
    }
};
