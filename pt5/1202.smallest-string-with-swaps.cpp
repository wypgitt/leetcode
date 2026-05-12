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
    string smallestStringWithSwaps(string s, vector<vector<int>>& pairs) {
        int n = s.size();
        DSU dsu(n);
        for (const auto& pair : pairs) dsu.unite(pair[0], pair[1]);

        unordered_map<int, vector<int>> groups;
        for (int i = 0; i < n; ++i) groups[dsu.find(i)].push_back(i);

        string answer = s;
        for (auto& [root, indices] : groups) {
            string chars;
            for (int index : indices) chars.push_back(s[index]);
            sort(indices.begin(), indices.end());
            sort(chars.begin(), chars.end());
            for (int i = 0; i < (int)indices.size(); ++i) {
                answer[indices[i]] = chars[i];
            }
        }

        return answer;
    }

private:
    struct DSU {
        vector<int> parent, rank;
        DSU(int n) : parent(n), rank(n, 0) {
            iota(parent.begin(), parent.end(), 0);
        }
        int find(int x) {
            if (parent[x] != x) parent[x] = find(parent[x]);
            return parent[x];
        }
        void unite(int a, int b) {
            int ra = find(a), rb = find(b);
            if (ra == rb) return;
            if (rank[ra] < rank[rb]) swap(ra, rb);
            parent[rb] = ra;
            if (rank[ra] == rank[rb]) ++rank[ra];
        }
    };
};

/*
Interview Explanation

Core idea:
Swap pairs define connected components of indices. Within a connected
component, any permutation of characters is reachable, so place the smallest
characters at the smallest indices.

C++ data structures:
- DSU/Union-Find groups swappable indices.
- unordered_map<int, vector<int>> stores indices per component.
- Sorting indices and characters gives the lexicographically smallest placement.

Algorithm:
1. Union every swappable pair.
2. Group indices by DSU root.
3. For each group, collect its characters.
4. Sort indices and characters, then assign smallest char to smallest index.

Correctness:
In a connected component, swaps along paths allow characters to move between
any two indices, so any permutation inside the component is possible. The
lexicographically smallest string is achieved independently per component by
putting the smallest available characters at the earliest indices.

Complexity:
DSU operations are nearly O(1). Sorting groups dominates: O(n log n) total.
Space is O(n).

Edge cases:
- No pairs returns the original string.
- Multiple disconnected components are optimized independently.
*/
