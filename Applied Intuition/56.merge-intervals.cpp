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
    vector<vector<int>> merge(vector<vector<int>>& intervals) {
        /*
        Approach:
        Sort intervals by start. The current interval either overlaps the last
        merged interval, in which case extend its end, or starts a new disjoint
        merged interval.

        Complexity: O(n log n) time and O(n) output space.
        */
        sort(intervals.begin(), intervals.end());
        vector<vector<int>> ans;
        for (const auto& interval : intervals) {
            if (ans.empty() || interval[0] > ans.back()[1]) ans.push_back(interval);
            else ans.back()[1] = max(ans.back()[1], interval[1]);
        }
        return ans;
    }
};
