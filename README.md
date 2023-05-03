# Table of content
- [Table of content](#table-of-content)
- [Overview](#overview)
- [Installation](#installation)
- [Usage tutorial](#usage-tutorial)
    - [Setup](#setup)
    - [Quick start](#quick-start)
    - [Groups](#groups)
    - [Functions with arguments](#functions-with-arguments)
    - [Aliases](#aliases)
- [Limitations](#limitations)
- [ToDo](#todo)

# Overview 	  
`dynamic_factory` is package for dynamic implementations of factory pattern. Currently it has implemented only one class. `FuncFactory` that is designed to work with functions. Project repo can be found on [github page]( https://github.com/WojciechBogobowicz/dynamic_factory) and package can be found on [pypi page]( https://pypi.org/project/dynamic-factory/#limitations ).



# Installation
Via pip:
```bash
pip install dynamic-factory
```
Via poetry:
```bash
poetry add dynamic-factory
```

# Usage tutorial

### Setup

Lets define two python files `./src1.py` and `./src2.py`


```python
# ./src1.py
def func1():
    print("greetings from src1 func1")


def func2(arg):
    print(f"greetings from src1 func2 with arg {arg}")


def func12():
    print("greetings from src1 func12")


def unregistered_func(arg):
    print(f"greetings from src1 unregistered_func with arg {arg}")
    
# ./src2.py
def func1():
    print("greetings from src2 func1")

def func2(arg):
    print(f"greetings from src2 func2 with arg {arg}")
```

### Quick start

If you want to register those functions in factory, decorate them with `@FuncFactory.register()` method.  
It has two arguments
- `alias` optional identifier that you can use instead of function name to execute function from factory level
- `group` help distinguish which factory should register which function. If you use only one factory, don't have to change it.
After that functions will be visible from factory.


```python
# ./src1.py
from dynamic_factory import FuncFactory


@FuncFactory.register()
def func1():
    print("greetings from src1 func1")


@FuncFactory.register(group="TWO")
def func2(arg):
    print(f"greetings from src1 func2 with arg {arg}")


@FuncFactory.register()
@FuncFactory.register(group="TWO")
def func12():
    print("greetings from src1 func12")


def unregistered_func(arg):
    print(f"greetings from src1 unregistered_func with arg {arg}")
    
# ./src2.py
from dynamic_factory import FuncFactory


@FuncFactory.register(alias="src2_func1")
def func1():
    print("greetings from src2 func1")

@FuncFactory.register(alias="func_two", group="TWO")
def func2(arg):
    print(f"greetings from src2 func2 with arg {arg}")
```

To create factory simply initialize `FuncFactory` object.


```python
from dynamic_factory import FuncFactory
import src1
import src2


base_factory = FuncFactory([src1])
print(
    "base factory registered aliases:", 
    *base_factory.registered_aliases
)

for alias in base_factory.registered_aliases:
    base_factory.execute(alias)
```

    base factory registered aliases: func1 func12
    greetings from src1 func1
    greetings from src1 func12


Note that `base_factory` don't recorded functions from `src2`, thats happened because `scr2` was not passed as argument in initialization. To fix that just extend `modules` list:


```python
func1_factory = FuncFactory([src1, src2])
print(
    "func1 factory registered aliases:", 
    *func1_factory.registered_aliases
)

for alias in func1_factory.registered_aliases:
    func1_factory.execute(alias)
```

    func1 factory registered aliases: func1 func12 src2_func1
    greetings from src1 func1
    greetings from src1 func12
    greetings from src2 func1


### Groups

Factories only register functions that belong to the same group as factory. If you want create more factories it may be good practice to define new groups. To define new group simply pass new unique string in register decorator. If you wish to create single function that belong to two group simply add two decorators like in `./src1.py:func12` example.


```python
func2_factory = FuncFactory([src1, src2], group="TWO")
print(
    "func2 factory registered aliases:", 
    *func2_factory.registered_aliases
)

func2_factory.execute("func12")
```

    func2 factory registered aliases: func12 func2 func_two
    greetings from src1 func12


### Functions with arguments
If you want execute functions with arguments pass them to `FuncFactory.execute` function as `args` and `kwargs`


```python

func2_factory.execute("func2", "argument")
func2_factory.execute("func_two", arg=123)
```

    greetings from src1 func2 with arg argument
    greetings from src2 func2 with arg 123


### Aliases
Default alias for function is its name. but if you prefer it is possible to change it during registration process with `alias` param. Sometimes it is necessary like in `./src2.py:func1` because it has the same name as `./src1.py:func1`, so without alias those functions would overwrite each other. 

# Limitations
Current implementation is adding field to functions that store record metadata, keep it in mind if you would do some advanced function manipulations like iteration trough `func.__dict__`

# ToDo
- [ ] Warn user if he have the same alias for two different functions.
- [ ] implement `__getitem__` that will access to factory function by alias.

