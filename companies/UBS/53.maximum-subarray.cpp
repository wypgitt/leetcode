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
    int maxSubArray(vector<int>& nums) {
        /*
        Approach:
        Kadane's algorithm keeps the best subarray sum ending at the current
        position. Either extend the previous subarray or start fresh at the
        current value, then update the global best.

        Complexity: O(n) time and O(1) space.
        */
        int current = nums[0], best = nums[0];
        for (int i = 1; i < (int)nums.size(); ++i) {
            current = max(nums[i], current + nums[i]);
            best = max(best, current);
        }
        return best;
    }
};
