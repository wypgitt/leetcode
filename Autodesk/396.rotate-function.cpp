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
    int maxRotateFunction(vector<int>& nums) {
        long long total = accumulate(nums.begin(), nums.end(), 0LL);
        long long cur = 0;
        int n = nums.size();
        for (int i = 0; i < n; ++i) cur += 1LL * i * nums[i];
        long long best = cur;
        for (int k = 1; k < n; ++k) {
            cur = cur + total - 1LL * n * nums[n - k];
            best = max(best, cur);
        }
        return static_cast<int>(best);
    }
};

/*
Interview explanation:
Compute F(0), then derive each next rotation in O(1): rotating right by one adds sum(nums) to all shifted indices, but the moved last element loses n*value.

C++ data structures: long long prevents intermediate overflow; vector<int>& avoids copying the input.

Edge cases: a one-element vector has F(0)=0 and the loop does not run.

Complexity: O(n) time and O(1) extra space.
*/
