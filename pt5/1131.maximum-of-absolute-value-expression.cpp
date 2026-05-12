#include <algorithm>
#include <array>
#include <climits>
#include <cmath>
#include <condition_variable>
#include <cstdlib>
#include <deque>
#include <functional>
#include <map>
#include <mutex>
#include <numeric>
#include <queue>
#include <set>
#include <sstream>
#include <stack>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

class Solution {
public:
    int maxAbsValExpr(vector<int>& arr1, vector<int>& arr2) {
        int answer = 0;
        vector<pair<int, int>> signs = {{1, 1}, {1, -1}, {-1, 1}, {-1, -1}};

        for (auto [s1, s2] : signs) {
            int low = INT_MAX;
            int high = INT_MIN;
            for (int i = 0; i < (int)arr1.size(); ++i) {
                int value = s1 * arr1[i] + s2 * arr2[i] + i;
                low = min(low, value);
                high = max(high, value);
            }
            answer = max(answer, high - low);
        }

        return answer;
    }
};

/*
Interview Explanation

Core idea:
|a-b| + |c-d| + |i-j| can be transformed by trying sign choices. Since the
index term can be represented as +i and choosing max-min covers order, four
combinations for arr1/arr2 signs are enough.

C++ data structures:
- A small vector of sign pairs enumerates transformations.
- Scalar min/max track the range of each transformed value.

Algorithm:
For each sign pair (s1, s2), compute value = s1*arr1[i] + s2*arr2[i] + i for
all i. The best pair for that transformation is max(value) - min(value).
Return the largest result across sign pairs.

Correctness:
Absolute values are maximized by choosing signs for each difference. Enumerating
the sign patterns covers all possibilities, and for a fixed pattern the best
i,j pair is simply the difference between maximum and minimum transformed
values.

Complexity:
O(n) time because there are only four sign patterns. O(1) space.

Edge cases:
- Arrays of length 1 return 0.
- Negative values are handled naturally by signed transformations.
*/
