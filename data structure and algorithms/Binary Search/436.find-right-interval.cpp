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
public:
    vector<int> findRightInterval(vector<vector<int>>& intervals) {
        vector<pair<int, int>> starts;
        for (int i = 0; i < (int)intervals.size(); ++i) starts.push_back({intervals[i][0], i});
        sort(starts.begin(), starts.end());
        vector<int> ans;
        ans.reserve(intervals.size());
        for (auto& interval : intervals) {
            auto it = lower_bound(starts.begin(), starts.end(), make_pair(interval[1], -1));
            ans.push_back(it == starts.end() ? -1 : it->second);
        }
        return ans;
    }
};

/*
Interview explanation:
Sort interval starts with original indices. For each end value, lower_bound finds the smallest start not less than the end.

C++ data structures: vector<pair<int,int>> sorts lexicographically and works directly with lower_bound.

Edge cases: no qualifying start returns -1.

Complexity: O(n log n) time and O(n) space.
*/
