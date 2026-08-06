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
    vector<int> lexicalOrder(int n) {
        vector<int> ans;
        ans.reserve(n);
        int cur = 1;
        for (int i = 0; i < n; ++i) {
            ans.push_back(cur);
            if (cur * 10 <= n) {
                cur *= 10;
            } else {
                while (cur % 10 == 9 || cur + 1 > n) cur /= 10;
                ++cur;
            }
        }
        return ans;
    }
};

/*
Interview explanation:
Lexicographic order is preorder traversal of an implicit 10-ary prefix tree. From x, visit child x*10 if it exists; otherwise climb until a next sibling x+1 is valid.

C++ data structures: vector<int> stores the answer and reserve(n) avoids repeated reallocations. No explicit trie is needed.

Edge cases: when a number ends in 9 or the next sibling exceeds n, integer division climbs to the parent prefix.

Complexity: O(n) time amortized and O(n) output space, with O(1) extra working memory.
*/
