## Court Transcript Pipeline Style Guide.

## General note

This style guide is intended to be supplemental to any native style guides relevant to particular languages or technologies. For example, in python code if there is any conflict between this document and PEP, ![PEP](https://peps.python.org/pep-0008/) should win out, and an issue should be created to update this document.

This style guide is not, therefore, exhaustive. Instead, it seeks to fill in finer details to ensure consistency across the project.

## File naming conventions

File names should, in general, be kebab case. Python modules should be snake case, and in the same vein as the general note, default to native naming conventions where they exist.

## Python code conventions

- All non-library modules should begin with a `main` function, called at the end with `if __name__ == "__main__"`.
- No library module should contain a `main` function or have an `if __name__ == "__main__"` block by the time pull requests are made. In general, testing should be done formally using a test file.
- Double quotes are the convention for string declaration, unless the string being declared includes double quotes, in which case single quotes are preferred to explicit escaping.
- All functions, with the exception of `main`, should have a docstring. The docstring should at least include a description of what the function returns. If the requirements for parameters are not clear from the function signature, and it would be impractical to make them so, then further details should prioritise terseness.
- All function parameters should be type hinted, but type hinting variables should be avoided outside of complex cases. (See ![PEP 484](https://peps.python.org/pep-0484/) and ![PEP 526](https://peps.python.org/pep-0526/) for further details)
- All functions should have a return type hint.
- All type hints for compound types should include type hints for contents, e.g. `dict[str, int]`, not `dict`.
