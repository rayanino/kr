Part C — Java Keywords (Meaning-First)

You will constantly see lines like:

```java
public class MyApp {
    public static void main(String[] args) { }
}
```

A good way to read Java:
**modifiers → what it is → name → parameters → body**.

---

## C1) Access modifiers (who is allowed to use this?)

### `public`

Accessible from anywhere.

### `private`

Accessible only inside the same class.

### `protected`

Accessible:

- inside the same class
- in the same package
- and in subclasses (even if subclass is in another package)

### (no keyword) = package-private (default)

If you write nothing, it’s accessible only within the same package.

Visibility from smallest → largest:
`private` → package-private → `protected` → `public`

---

## C2) `static` (belongs to the class, not an object)

### Instance vs static

- **instance member**: belongs to each object (each object has its own copy)
- **static member**: belongs to the class (one shared copy)

### `static` field

```java
static int counter = 0;
```

One `counter` shared across all objects.

### `static` method

```java
static void log(String msg) { ... }
```

Call without creating an object:

```java
MyClass.log("hi");
```

Rule:

- A `static` method cannot directly use instance fields/methods because it has no specific object (`this`).

---

## C3) Return types: `void` vs returning a value

### `void`

Method returns nothing.

```java
void printHello() {
    System.out.println("Hello");
}
```

### Returning a value

```java
int add(int a, int b) {
    return a + b;
}
```

---

## C4) `return` (send back a value / stop method)

- returns a value in non-void methods
- may be used alone in `void` methods to exit early

```java
return 5;
return;
```

Also: `return` ends the method immediately.

---

## C5) `class` (define a type)

```java
public class Car { ... }
```

Defines:

- fields (data)
- methods (behavior)
- constructors (object creation rules)

---

## C6) `new` (create an object)

```java
Car c = new Car();
```

Allocates a new object and calls its constructor.

---

## C7) `this` (the current object)

Inside instance methods/constructors, `this` refers to the current object.

```java
class Car {
    String color;

    Car(String color) {
        this.color = color; // field vs parameter
    }
}
```

---

## C8) `main` (program entry point)

The JVM looks for:

```java
public static void main(String[] args)
```

Meaning:

- `public`: JVM can call it
- `static`: JVM doesn’t need to create an object
- `void`: returns nothing to JVM
- `String[] args`: command-line arguments

---

## C9) Primitive types (not objects)

Common primitives:

- `int` (whole numbers)
- `double` (decimals)
- `boolean` (true/false)
- `char` (single character)
- `long`, `short`, `byte`, `float`

Primitives cannot be `null`.

---

## C10) Reference types (objects)

Examples:

- `String`
- `Car`
- `Integer` (wrapper object)
- arrays like `String[]`

Reference types can be `null`.

---

## C11) `null` (no object)

`null` means the reference points to nothing.

Using members on `null` triggers `NullPointerException`.

---

## C12) `final` (locked)

### `final` variable

Cannot be reassigned:

```java
final int x = 5;
// x = 6;  // not allowed
```

### `final` method

Cannot be overridden.

### `final` class

Cannot be subclassed.

---

## C13) `abstract` (incomplete on purpose)

### `abstract` class

Cannot be instantiated directly.

### `abstract` method

No body; subclasses must implement.

```java
abstract class Animal {
    abstract void makeSound();
}
```

---

## C14) `extends` vs `implements`

### `extends`

Subclassing:

```java
class Dog extends Animal { }
```

### `implements`

Interface contract:

```java
class Worker implements Runnable { }
```

---

## C15) `interface` (a contract)

An interface describes required methods/capabilities.
Classes implementing it promise to provide them.

---

## C16) `import` (bring types into scope)

Instead of writing fully qualified names:

```java
java.util.ArrayList list = new java.util.ArrayList();
```

You do:

```java
import java.util.ArrayList;
```

---

## C17) `package` (declare the namespace)

At the top of a file:

```java
package com.example.app;
```

Must match folder path under the source root.

---

## C18) `var` (type inference for local variables)

```java
var name = "Rayane"; // inferred as String
```

Not dynamic typing. Only for **local variables**, not fields/parameters.

---

## C19) `throw` vs `throws` (exceptions)

### `throw`

Raise an exception:

```java
throw new IllegalArgumentException("bad input");
```

### `throws`

Declare that a method may throw:

```java
void read() throws IOException { ... }
```

---

# Part D — Decoding Typical Java Lines

## Example 1

```java
private static final int MAX = 10;
```

- `private`: only this class can see it
- `static`: shared at class-level
- `final`: cannot be reassigned
- `int`: primitive number type
- `MAX`: name

## Example 2

```java
public String getName() { return name; }
```

- `public`: any class can call it
- `String`: return type
- `getName`: method name
- returns `name`

---

# Part E — What to Master First (minimal set)

1. `public` / `private` / default visibility
2. `static` (class-level vs object-level)
3. return types (`void`, `int`, `String`, …)
4. `return`
5. `class`, `new`, `this`
6. `package`, `import`
7. classpath (conceptually)

---

# Part F — One-sentence mental model

- You write `.java` in source roots.
- Packages map to folders under the source root.
- `javac` compiles `.java` into `.class` (bytecode).
- The JVM loads `.class` from output + jars using the classpath and runs the program.
- Keywords like `public/private/static/void` describe access, ownership (class vs object), and method behavior.