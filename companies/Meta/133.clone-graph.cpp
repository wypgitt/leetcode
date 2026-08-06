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

// Definition for a Node.
// class Node {
// public:
//     int val;
//     vector<Node*> neighbors;
//     Node() : val(0), neighbors(vector<Node*>()) {}
//     Node(int _val) : val(_val), neighbors(vector<Node*>()) {}
//     Node(int _val, vector<Node*> _neighbors) : val(_val), neighbors(_neighbors) {}
// };


class Solution {
public:
    Node* cloneGraph(Node* node) {
        /*
        Approach: DFS clone with memoization. When a node is first seen, create
        its clone and store it in a hash map before cloning neighbors. Storing
        before recursion handles cycles correctly.

        C++ notes: unordered_map<Node*, Node*> maps original graph node pointers
        to cloned node pointers.
        Complexity: O(V + E) time, O(V) space.
        */
        unordered_map<Node*, Node*> clones;
        function<Node*(Node*)> clone = [&](Node* cur) -> Node* {
            if (!cur) return nullptr;
            if (clones.count(cur)) return clones[cur];
            Node* copied = new Node(cur->val);
            clones[cur] = copied;
            for (Node* nei : cur->neighbors) copied->neighbors.push_back(clone(nei));
            return copied;
        };
        return clone(node);
    }
};
