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
    int triangleNumber(vector<int>& nums) {
        sort(nums.begin(), nums.end());
        int ans = 0, n = nums.size();
        for (int k = n - 1; k >= 2; --k) {
            int i = 0, j = k - 1;
            while (i < j) {
                if (nums[i] + nums[j] > nums[k]) {
                    ans += j - i;
                    --j;
                } else {
                    ++i;
                }
            }
        }
        return ans;
    }
};

/*
Interview explanation:
After sorting, choose each largest side nums[k]. If nums[i]+nums[j] > nums[k], then every index from i through j-1 with j also works.

C++ data structures: sorted vector and two pointers.

Edge cases: zeros naturally fail the strict triangle inequality.

Complexity: O(n^2) time after sorting and O(1) extra space.
*/
