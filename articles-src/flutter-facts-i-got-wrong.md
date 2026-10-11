---
title: 4 Flutter facts I got wrong until I wrote the tests
description: Lazy lists that build 5,000 items, popUntil typos that empty the stack, const widgets that are not identical, and secrets in --dart-define, each proven by a Flutter test.
date: 2026-10-11
---

I've been building Algoistan, a free animated course that explains how Flutter works inside. My rule for the Flutter section was simple: no claim goes on a page unless a `flutter test` proves it. 317 tests later, four of my "facts" turned out to be wrong or incomplete.

### 1. Without `itemExtent`, one jump can build thousands of list items

```dart
ListView.builder(
  controller: controller,
  itemCount: 10000,
  itemExtent: 80, // without this line, see below
  itemBuilder: (context, i) => ListItem(i),
);

controller.jumpTo(400000); // item 5000 at the top
```

I expected a lazy list to build only what's on screen. With every item 80 px tall and the list jumping to item 5,000, the test counted the `itemBuilder` calls: **5,000 without `itemExtent`, 18 with it** (`prototypeItem` also gave 18). Without a fixed extent, Flutter has to lay out every item between the old and new position to know where item 5,000 starts.

### 2. `popUntil` with a typo doesn't throw — it empties the stack

```dart
Navigator.of(context).popUntil(ModalRoute.withName('/hmoe')); // meant '/home'
```

No route matches, so `popUntil` keeps popping — past `/home`, past the first route — and leaves an empty navigator, without any exception. Worth a guard in code review.

### 3. Two identical `const` widgets aren't always the same object

```dart
final a = const Text('Hi');
final b = const Text('Hi');
print(identical(a, b)); // false in debug and flutter test, true in release
```

In debug builds Flutter's widget-creation tracking quietly records *where* each widget was written, so two `const` widgets on different lines differ. In release they're canonicalised into one object. If you reason about rebuilds using `identical`, test in the mode you care about.

### 4. `--dart-define` is not a place for secrets

```dart
const apiKey = String.fromEnvironment('API_KEY');
```

Once your code actually uses `apiKey`, the value is compiled into the release binary and can be read straight out of it. (If you only use, say, its length, the compiler folds it away — which is why "I checked and it wasn't there" can mislead you.) Anything you ship can be extracted; keep real secrets on a server.

---

Each of these comes with an animation you can drive with your own input — keys and State, Row's flex layout, a frame timeline, lazy list building, the Navigator stack, deep links — in the six lessons of Level 12:

https://algoistan.flutterdev.in/flutter/f01-widgets-elements.html

The same site also has a problem-solving level — about 90 classic interview problems grouped by pattern, from Two Sum to N-Queens, each animated and solved in tested Dart: https://algoistan.flutterdev.in/problems/p01-arrays-hashing.html

The site is free, needs no sign-up and works offline. Feedback and corrections welcome in the comments.
