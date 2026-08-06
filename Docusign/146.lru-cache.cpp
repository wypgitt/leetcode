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


class LRUCache {
    struct Node {
        int key;
        int value;
        Node* prev;
        Node* next;
        Node(int k = 0, int v = 0) : key(k), value(v), prev(nullptr), next(nullptr) {}
    };

    int capacity;
    unordered_map<int, Node*> nodes;
    Node* head;
    Node* tail;

    void remove(Node* node) {
        node->prev->next = node->next;
        node->next->prev = node->prev;
    }

    void addToBack(Node* node) {
        Node* last = tail->prev;
        last->next = node;
        node->prev = last;
        node->next = tail;
        tail->prev = node;
    }

    void markUsed(Node* node) {
        remove(node);
        addToBack(node);
    }

public:
    LRUCache(int capacity) : capacity(capacity) {
        /*
        Approach: hash table plus doubly linked list. The hash table maps keys
        to list nodes for O(1) access. The list is ordered from least recently
        used after head to most recently used before tail.

        C++ notes: custom Node* pointers implement the doubly linked list, while
        unordered_map<int, Node*> replaces Python's dict.
        Complexity: get and put are O(1) average time, O(capacity) space.
        */
        head = new Node();
        tail = new Node();
        head->next = tail;
        tail->prev = head;
    }

    int get(int key) {
        if (!nodes.count(key)) return -1;
        Node* node = nodes[key];
        markUsed(node);
        return node->value;
    }

    void put(int key, int value) {
        if (nodes.count(key)) {
            Node* node = nodes[key];
            node->value = value;
            markUsed(node);
            return;
        }
        Node* node = new Node(key, value);
        nodes[key] = node;
        addToBack(node);
        if ((int)nodes.size() > capacity) {
            Node* lru = head->next;
            remove(lru);
            nodes.erase(lru->key);
            delete lru;
        }
    }
};
