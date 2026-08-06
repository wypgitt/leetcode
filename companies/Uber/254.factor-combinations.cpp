#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;


class Solution {
public:
    vector<vector<int>> getFactors(int n) {
        /*
        Approach: backtrack nondecreasing factors. For each factor dividing the
        current target, output the current path plus factor and target/factor,
        then continue factoring target/factor starting at the same factor.

        Complexity: output-sensitive exponential time, O(log n) recursion depth
        for factor chains.
        */
        vector<vector<int>> ans;
        vector<int> path;
        function<void(int, int)> dfs = [&](int start, int target) {
            for (int factor = start; (long long)factor * factor <= target; ++factor) {
                if (target % factor != 0) continue;
                path.push_back(factor);
                vector<int> combo = path;
                combo.push_back(target / factor);
                ans.push_back(combo);
                dfs(factor, target / factor);
                path.pop_back();
            }
        };
        dfs(2, n);
        return ans;
    }
};
