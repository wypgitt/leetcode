package main

import "strings"

type FileSystem struct {
	values map[string]int
}

func Constructor() FileSystem {
	return FileSystem{values: map[string]int{"": -1}}
}

func (fs *FileSystem) CreatePath(path string, value int) bool {
	if _, exists := fs.values[path]; exists {
		return false
	}
	parent := path[:strings.LastIndex(path, "/")]
	if _, exists := fs.values[parent]; !exists {
		return false
	}
	fs.values[path] = value
	return true
}

func (fs *FileSystem) Get(path string) int {
	if value, exists := fs.values[path]; exists {
		return value
	}
	return -1
}

