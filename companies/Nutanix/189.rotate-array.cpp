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
    void rotate(vector<int>& nums, int k) {
        /*
        Approach: reverse the whole array, reverse the first k elements, then
        reverse the remaining n-k elements. This moves the last k elements to the
        front while preserving both groups' internal order.

        Complexity: O(n) time, O(1) space.
        */
        int n = nums.size();
        k %= n;
        reverse(nums.begin(), nums.end());
        reverse(nums.begin(), nums.begin() + k);
        reverse(nums.begin() + k, nums.end());
    }
};
