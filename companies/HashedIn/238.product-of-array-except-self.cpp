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
    vector<int> productExceptSelf(vector<int>& nums) {
        /*
        Approach: first pass stores product of all numbers before i. Second pass
        multiplies by product of all numbers after i. This avoids division and
        handles zeros naturally.

        Complexity: O(n) time, O(1) extra space excluding output.
        */
        vector<int> ans(nums.size(), 1);
        int prefix = 1;
        for (int i = 0; i < (int)nums.size(); ++i) {
            ans[i] = prefix;
            prefix *= nums[i];
        }
        int suffix = 1;
        for (int i = (int)nums.size() - 1; i >= 0; --i) {
            ans[i] *= suffix;
            suffix *= nums[i];
        }
        return ans;
    }
};
