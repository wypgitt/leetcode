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
    int numRollsToTarget(int n, int k, int target) {
        const int MOD = 1'000'000'007;
        vector<int> dp(target + 1, 0);
        dp[0] = 1;

        for (int dice = 0; dice < n; ++dice) {
            vector<int> next(target + 1, 0);
            for (int sum = 0; sum <= target; ++sum) {
                if (dp[sum] == 0) continue;
                for (int face = 1; face <= k && sum + face <= target; ++face) {
                    next[sum + face] = (next[sum + face] + dp[sum]) % MOD;
                }
            }
            dp.swap(next);
        }

        return dp[target];
    }
};

/*
Interview Explanation

Core idea:
Use DP over dice count and current sum. Each die adds one face value from 1..k.

C++ data structures:
- vector<int> dp[sum] stores ways after processing some number of dice.
- A second vector next builds the next layer.

Algorithm:
1. Start with dp[0] = 1.
2. For each die, distribute every reachable sum to sum+face.
3. Apply modulo after each addition.
4. Return ways to reach target after n dice.

Correctness:
Every roll sequence has a unique previous sum before the last die and one last
face value. The transition enumerates all such choices, so it counts exactly
all sequences reaching each sum.

Complexity:
O(n * target * k) time and O(target) space.

Edge cases:
- Impossible target remains 0.
- n = 1 counts faces directly.
*/
