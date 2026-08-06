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
    int minMoves2(vector<int>& nums) {
        sort(nums.begin(), nums.end());
        int median = nums[nums.size() / 2];
        long long moves = 0;
        for (int x : nums) moves += llabs((long long)x - median);
        return (int)moves;
    }
};

/*
Interview explanation:
The sum of absolute distances is minimized at any median. Sort to get a median, then sum distances to it.

C++ data structures: sorting is in-place on vector<int>; long long safely accumulates distances.

Edge cases: for even length, either middle value is optimal.

Complexity: O(n log n) time and O(1) extra space beyond sort internals.
*/
