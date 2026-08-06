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
    vector<int> twoSum(vector<int>& numbers, int target) {
        /*
        Approach: two pointers on the sorted array. If the sum is too small,
        increase the left pointer; if too large, decrease the right pointer.

        Complexity: O(n) time, O(1) space.
        */
        int left = 0, right = numbers.size() - 1;
        while (left < right) {
            int total = numbers[left] + numbers[right];
            if (total == target) return {left + 1, right + 1};
            if (total < target) ++left;
            else --right;
        }
        return {};
    }
};
