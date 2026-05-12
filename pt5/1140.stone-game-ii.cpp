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
    int stoneGameII(vector<int>& piles) {
        int n = piles.size();
        suffix.assign(n + 1, 0);
        for (int i = n - 1; i >= 0; --i) suffix[i] = suffix[i + 1] + piles[i];
        memo.assign(n, vector<int>(n + 1, -1));
        return dfs(0, 1);
    }

private:
    vector<int> suffix;
    vector<vector<int>> memo;

    int dfs(int index, int m) {
        int n = suffix.size() - 1;
        if (index >= n) return 0;
        if (2 * m >= n - index) return suffix[index];
        if (memo[index][m] != -1) return memo[index][m];

        int best = 0;
        for (int x = 1; x <= 2 * m; ++x) {
            int opponent = dfs(index + x, max(m, x));
            best = max(best, suffix[index] - opponent);
        }
        return memo[index][m] = best;
    }
};

/*
Interview Explanation

Core idea:
This is minimax DP. From state (index, M), the current player chooses x piles
and then the opponent gets an optimal score from the remaining suffix.

C++ data structures:
- suffix[i] stores total stones from i to end.
- memo[index][M] caches the best current-player score for each state.

Algorithm:
1. Precompute suffix sums.
2. dfs(index, M) returns the maximum stones current player can get.
3. If the player can take all remaining piles, return suffix[index].
4. Otherwise try x from 1 to 2M and maximize suffix[index] - opponentScore.

Correctness:
After choosing x, all remaining stones are split between the opponent and the
current player. If the opponent optimally obtains dfs(index+x, max(M,x)), the
current player gets the remaining suffix total minus that amount. Trying every
legal x gives the optimal move.

Complexity:
There are O(n^2) states and each tries O(n) moves, so O(n^3) time worst case,
with O(n^2) space. n is small enough for this DP.

Edge cases:
- If 2M covers the suffix, take all piles.
- Single pile returns that pile.
*/
