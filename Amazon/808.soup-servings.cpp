#include <algorithm>
#include <array>
#include <cmath>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <random>
#include <regex>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

class Solution {
    vector<vector<double>> memo;
    vector<vector<int>> ops{{4,0},{3,1},{2,2},{1,3}};

    double dp(int a, int b) {
        if (a <= 0 && b <= 0) return 0.5;
        if (a <= 0) return 1.0;
        if (b <= 0) return 0.0;
        double& res = memo[a][b];
        if (res >= 0.0) return res;
        res = 0.0;
        for (auto& op : ops) res += 0.25 * dp(a - op[0], b - op[1]);
        return res;
    }

public:
    double soupServings(int n) {
        if (n > 4800) return 1.0;
        int units = (n + 24) / 25;
        memo.assign(units + 1, vector<double>(units + 1, -1.0));
        return dp(units, units);
    }
};

/*
Interview explanation:
Scale milliliters into 25mL units. dp(a,b) is the target probability from remaining units, averaged over the four serving operations.

C++ data structures: vector<vector<double>> memo caches probabilities; -1 marks uncomputed states.

Edge cases: simultaneous empty contributes 0.5. For n>4800 the probability is within 1e-5 of 1.

Complexity: O(u^2) time and space below the cutoff, where u=ceil(n/25).
*/
