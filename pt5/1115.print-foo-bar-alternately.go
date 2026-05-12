package main

type FooBar struct {
	n       int
	fooTurn chan struct{}
	barTurn chan struct{}
}

func Constructor(n int) FooBar {
	fooTurn := make(chan struct{}, 1)
	barTurn := make(chan struct{}, 1)
	fooTurn <- struct{}{}
	return FooBar{n: n, fooTurn: fooTurn, barTurn: barTurn}
}

func (fb *FooBar) foo(printFoo func()) {
	for i := 0; i < fb.n; i++ {
		<-fb.fooTurn
		printFoo()
		fb.barTurn <- struct{}{}
	}
}

func (fb *FooBar) bar(printBar func()) {
	for i := 0; i < fb.n; i++ {
		<-fb.barTurn
		printBar()
		fb.fooTurn <- struct{}{}
	}
}

func (fb *FooBar) Foo(printFoo func()) {
	fb.foo(printFoo)
}

func (fb *FooBar) Bar(printBar func()) {
	fb.bar(printBar)
}
