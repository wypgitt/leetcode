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
    vector<vector<int>> subsets(vector<int>& nums) {
        /*
        Approach:
        Start with the empty subset. For each number, copy every subset built so
        far and append the number to the copy. This models the include/exclude
        choice for each element.

        Complexity: O(2^n * n) time and O(2^n * n) output space.
        */
        vector<vector<int>> ans(1);
        for (int num : nums) {
            int size = (int)ans.size();
            for (int i = 0; i < size; ++i) {
                vector<int> next = ans[i];
                next.push_back(num);
                ans.push_back(move(next));
            }
        }
        return ans;
    }
};
