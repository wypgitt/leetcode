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
    vector<vector<int>> insert(vector<vector<int>>& intervals, vector<int>& newInterval) {
        /*
        Approach:
        Because intervals are sorted and non-overlapping, first copy all
        intervals ending before newInterval. Merge every overlapping interval
        into newInterval, append it, then copy the remaining intervals.

        Complexity: O(n) time and O(n) output space.
        */
        vector<vector<int>> ans;
        int i = 0, n = (int)intervals.size();
        while (i < n && intervals[i][1] < newInterval[0]) ans.push_back(intervals[i++]);
        while (i < n && intervals[i][0] <= newInterval[1]) {
            newInterval[0] = min(newInterval[0], intervals[i][0]);
            newInterval[1] = max(newInterval[1], intervals[i][1]);
            ++i;
        }
        ans.push_back(newInterval);
        while (i < n) ans.push_back(intervals[i++]);
        return ans;
    }
};
