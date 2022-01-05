Sandbox for managing WDI metadata in Git(?)

**NOTE:** `make.py` uses a custom variant of PyYAML available
[here](https://github.com/tgherzog/pyyaml). The variant provides
a "strict_whitespace" option that can be set to False to produce
cleaner-looking multi-line text values. I intend to submit this
as a pull request since other users have
[raised this as an issue](https://github.com/yaml/pyyaml/issues/402).
For now, you need to either include/clone this module in your working directory
or install it into a virtual environment. Alternatively, you can use the
`--compatible` option in `make.py` to disable the "strict_whitespace" parameter
in `make.py` and suffer through with less legible yaml output.

### References ###

* [YAML Syntax](https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html):
  The Ansible documentation has a nice, consise syntax summary, including "gotchas."
