import inspect
from typing import Iterable, Union, Callable
from dataclasses import dataclass
import warnings


__all__ = ["FuncFactory"]
DEFAULT_GROUP_NAME = "DEFAULT"

class FuncFactory:
    """Dynamic implementation of factory design pattern,
     that is designed to work with functions.
    """
    _all_groups = set()
    
    def __init__(self, modules: Iterable, group: str = DEFAULT_GROUP_NAME) -> None:
        """Dynamic implementation of factory design pattern,
     that is designed to work with functions.

        Args:
            modules (Iterable): List of all modules where registered functions persist.
            group (str, optional): If you need more than one factory, 
                you can distinguish between them by creating different groups
                in this arg, and during registration. Defaults to 'DEFAULT'.
        """
        self.group = group
        self.func_record = self._create_record_name(group)
        self.modules = modules
        self._registry = self._load_registry(modules)
        self.warn_if_registry_empty()
    
    def warn_if_registry_empty(self) -> None:
        message = """Factory do not register any function.
        If it is unintentional check if factory group is the same as register group,
        modules with registered functions are passed to 'modules' arg
        and make sure you don't forgot brackets in decorator '@FuncFactory.register()'."""
        if len(self.registered_aliases) == 0:
            warnings.warn(message, RuntimeWarning)
    
    @property
    def registered_aliases(self) -> list[str]:
        """Return all registered functions aliases.

        Returns:
            list[str]: All aliases tracked by factory.
        """
        return list(self._registry.keys())

    def execute(self, alias: str, *args, **kwargs) -> any:
        """Execute function registered with given alias, with specified args, and kwargs.

        Args:
            alias (str): Alias of function specified in register method, or function name.

        Returns:
            any: Output from function.
        """
        return self._registry[alias](*args, **kwargs)

    def get(self, alias: str) -> Callable:
        """Return function that is stored with given alias.

        Args:
            alias (str): fuction alias or name.

        Returns:
            Callable: Stored function
        """
        return self._registry[alias]

    def _load_registry(self, modules) -> dict[str, Callable]:
        """Load all registered functions and store them as dict.

        Args:
            modules (list[Modules]): modules objects with registered functions.

        Returns:
            dict[str, Callable]: Dict with registered functions in values,
            and their aliases as keys. 
        """
        functions = self._load_registered_functions(modules)
        return self._parse_to_dict(functions)

    def _load_registered_functions(self, modules) -> list[Callable]:
        """Load all registered functions and store them as list.

        Args:
            modules (Iterable): List of all modules where registered functions persist.

        Returns:
            list[Callable]: list of all loaded functions
        """
        functions = []
        for module in modules:
            functions.extend(
                inspect.getmembers(
                    module,
                    self._module_member_predicate
                )
            )
        return [f[1] for f in functions]

    def _module_member_predicate(self, member) -> bool:
        """Define conditions that module member have to meet.

        Args:
            member (Any): Module member

        Returns:
            bool: True if member is registered function, else false.
        """
        if not inspect.isfunction(member):
            return False
        return hasattr(member, self.func_record)

    def _parse_to_dict(self, functions) -> dict:
        """Get list of registered functions, and turn them into dict with aliases as keys.

        Args:
            functions (list[Callable]): list of registered functions.

        Returns:
            dict[str, Callable]: Dict with registered functions in values,
            and their aliases as keys. 
        """
        output = dict()
        for func in functions:
            record: _Record = getattr(func, self.func_record)
            alias = record.ALIAS
            output[alias] = func
        return output

    @classmethod
    def register(cls, alias: Union[str, None] = None, group: str = DEFAULT_GROUP_NAME):
        """Decorator that make function visible for factory.

        Args:
            alias (Union[str, None], optional): Identifier of function used during execution.
                If none, function name will be used. Defaults to None.
            group (str, optional): Group identifier that will be used by factories
                during registered functions loading. Defaults to 'DEFAULT'.
        """
        cls._all_groups.add(group)
        def wrapper(func: Callable) -> Callable:
            nonlocal alias
            nonlocal group
            record_name = cls._create_record_name(group)
            if not alias:
                alias = func.__name__
            
            if hasattr(func, record_name):
                raise RuntimeError(
                    f"Function that you want register already have attribute {record_name}. "
                    "This attribute would be overwritten during register process. "
                    "Error was risen to prevent it. "
                    "Changing FuncFactory group parameter should fix this problem."
                )
            record = _Record(group, alias)
            setattr(func, record_name, record)
            return func
        return wrapper

    @staticmethod
    def _create_record_name(group: str) -> str:
        """Create name of attribute that will be added to registered functions.

        Args:
            group (str): Group name that function belong to.

        Returns:
            str: attribute name.
        """
        return f"__RECORD_OF_{group}"


@dataclass(frozen=True)
class _Record:
    """Store information data about record.
    """
    GROUP: str
    ALIAS: str