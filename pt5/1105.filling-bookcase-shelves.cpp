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
    int minHeightShelves(vector<vector<int>>& books, int shelfWidth) {
        int n = books.size();
        vector<int> dp(n + 1, INT_MAX / 2);
        dp[0] = 0;

        for (int end = 1; end <= n; ++end) {
            int width = 0;
            int height = 0;
            for (int start = end; start >= 1; --start) {
                width += books[start - 1][0];
                if (width > shelfWidth) break;
                height = max(height, books[start - 1][1]);
                dp[end] = min(dp[end], dp[start - 1] + height);
            }
        }

        return dp[n];
    }
};

/*
Interview Explanation

Core idea:
The last shelf determines the DP transition. If books start..end are placed on
the final shelf, the total height is best height before start plus the maximum
book height on this shelf.

C++ data structures:
- vector<int> dp where dp[i] is the minimum height for the first i books.
- Scalar width and height are maintained while extending the last shelf
  backward.

Algorithm:
1. Let dp[0] = 0.
2. For each end position, try every possible start position for the last shelf.
3. Stop when shelf width is exceeded.
4. Update dp[end] with dp[start-1] + max height on that shelf.

Correctness:
Every valid arrangement of the first end books has some last shelf containing a
contiguous suffix of books. The recurrence tries every suffix that fits and
combines it with the optimal arrangement of the preceding books, so it returns
the global optimum.

Complexity:
O(n^2) time in the worst case and O(n) space.

Edge cases:
- A single book returns its height.
- A shelf that can fit many books is explored by the backward loop.
- Width overflow is avoided because constraints are small and int is enough.
*/
