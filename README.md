<h1 align="center" style="border-bottom: none;">⚙&nbsp;📝&nbsp;&nbsp;Settings&nbsp;DocGen&nbsp;&nbsp;📝&nbsp;⚙</h1>
<h3 align="center">A command line tool for generating Markdown documentation and .env files from <a href="https://pydantic-docs.helpmanual.io/usage/settings">pydantic.BaseSettings</a>.</h3>

<p align="center">
    <a href="https://app.circleci.com/pipelines/github/radeklat/settings-doc?branch=main">
        <img alt="CircleCI" src="https://img.shields.io/circleci/build/github/radeklat/settings-doc">
    </a>
    <a href="https://app.codecov.io/gh/radeklat/settings-doc/">
        <img alt="Codecov" src="https://img.shields.io/codecov/c/github/radeklat/settings-doc">
    </a>
    <a href="https://github.com/radeklat/settings-doc/tags">
        <img alt="GitHub tag (latest SemVer)" src="https://img.shields.io/github/tag/radeklat/settings-doc">
    </a>
    <img alt="Maintenance" src="https://img.shields.io/maintenance/yes/2024">
    <a href="https://github.com/radeklat/settings-doc/commits/main">
        <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/radeklat/settings-doc">
    </a>
    <a href="https://pypistats.org/packages/settings-doc">
        <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/settings-doc">
    </a>
    <a href="https://github.com/radeklat/settings-doc/blob/main/LICENSE">
        <img alt="PyPI - License" src="https://img.shields.io/pypi/l/settings-doc">
    </a>
    <a href="https://www.python.org/doc/versions/">
        <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/settings-doc">
    </a>
    <a href="https://pydantic.dev">
        <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json" alt="Pydantic Version 2" style="max-width:100%;">
    </a>
</p>

The same way you are able to generate OpenAPI documentation from [`pydantic.BaseModel`](https://pydantic-docs.helpmanual.io/usage/models/), `settings-doc` allows you to generate documentation from [`pydantic_settings.BaseSettings`](https://docs.pydantic.dev/latest/usage/pydantic_settings/).

It is powered by the [Jinja2](https://jinja.palletsprojects.com/en/latest/) templating engine and [Typer](https://typer.tiangolo.com/) framework. If you don't like the built-in templates, you can easily modify them or write completely custom ones. All attributes of the [`BaseSettings`](https://docs.pydantic.dev/latest/usage/pydantic_settings/) models are exposed to the templates.

<!--
    How to generate TOC from PyCharm:
    https://github.com/vsch/idea-multimarkdown/wiki/Table-of-Contents-Extension
-->
[TOC levels=1,2 markdown formatted bullet hierarchy]: # "Table of content"

# Table of content
- [Installation](#installation)
- [Usage](#usage)
  - [Minimal example](#minimal-example)
  - [Class auto-discovery](#class-auto-discovery)
  - [Adding more information](#adding-more-information)
  - [Updating existing documentation](#updating-existing-documentation)
- [Advanced usage](#advanced-usage)
  - [Custom templates](#custom-templates)
  - [Custom settings attributes in templates](#custom-settings-attributes-in-templates)
  - [As a pre-commit hook](#as-a-pre-commit-hook)
- [Features overview](#features-overview)
  - [Markdown](#markdown)
  - [.env](#env)

# Installation

```
pip install settings-doc
```

# Usage

See `settings-doc --help` for all options.

## Minimal example

Let's assume the following [`BaseSettings`](https://docs.pydantic.dev/latest/usage/pydantic_settings/) in `src/settings.py` of a project:

```python
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    logging_level: str
```

You can generate a Markdown documentation into stdout with:

```shell script
settings-doc generate --class src.settings.AppSettings --output-format markdown
```

Which will output:

```markdown
# `LOGGING_LEVEL`

**Required**
```

Similarly, you can generate a `.env` file for local development with:

```shell script
settings-doc generate --class src.settings.AppSettings --output-format dotenv
```

Which will output:

```dotenv
LOGGING_LEVEL=

```

## Class auto-discovery

If you have a module with a single settings class or want to load multiple classes at once as a source, you can also use the `--module` option. The following example works exactly like the one above and will use the `AppSettings` class automatically.

```shell script
settings-doc generate --module src.settings --output-format dotenv
```

If multiple classes contain a field with the same name, all instances will appear in the output.

## Adding more information

You can add any extra field parameters to the settings. By default, `settings-doc` will utilise the default value, whether the parameter is required or optional, description, example value, and list of possible values:

```python
from pydantic_settings import BaseSettings, Field

class AppSettings(BaseSettings):
    logging_level: str = Field(
        "WARNING",
        description="Log level.",
        example="`WARNING`",
        possible_values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
```

Which will generate the following markdown:

```markdown
# `LOGGING_LEVEL`

*Optional*, default value: `WARNING`

Log level.

## Examples

`WARNING`

## Possible values

`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
```

or `.env` file:

```dotenv
# Log level.
# Possible values:
#   `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
# LOGGING_LEVEL=WARNING
```

You can find even more complex usage of `settings-doc` in [one of my other projects](https://github.com/radeklat/mqtt-influxdb-gateway/blob/main/README.md#environment-variables).

## Updating existing documentation

It is possible to generate documentation into an existing document. To fit with the heading structure, you can adjust the heading levels with `--heading-offset`. Additionally, you can specify the location where to generate the documentation with two marks set by `--between <START MARK> <END MARK>`.

Let's assume your `README.md` looks like this:

```markdown
# My app

This app is distributes as a docker image and configurable via environment variables. See the list below.

# Environment variables
<!-- generated env. vars. start -->
<!-- generated env. vars. end -->
```

When you run:

```shell script
settings-doc generate \
  --class src.settings.AppSettings \
  --output-format markdown \ 
  --update README.md \
  --between "<!-- generated env. vars. start -->" "<!-- generated env. vars. end -->" \
  --heading-offset 1
```

the updated `README.md` will get only the specified location overwritten:

```markdown
# My app

This app is distributes as a docker image and configurable via environment variables. See the list below.

# Environment variables
<!-- generated env. vars. start -->
## `LOGGING_LEVEL`

*Optional*, default value: `WARNING`

Log level.

### Examples

`WARNING`

### Possible values

`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
<!-- generated env. vars. end -->
```

# Advanced usage

## Custom templates

`settings-doc` comes with a few built-in templates. You can override them or write completely new ones.

To just modify the existing ones:
1. Copy the built-in templates into a new directory:
   ```shell script
   mkdir custom_templates
   settings-doc templates --copy-to custom_templates
   ```
2. Modify the template copies in `custom_templates` to suit your needs. You can keep only the modified ones as `settings-doc` always falls back to the built-in ones.
3. Use them when generating the documentation:
   ```shell script
   settings-doc generate \
     --class src.settings.AppSettings \
     --output-format dotenv \
     --templates custom_templates
   ```

To create new ones, create a folder and then a Jinja2 template with a file names `<OUTPUT_FORMAT>.jinja`. Then simply reference both in the command line options:

```shell script
mkdir custom_templates

echo "{{ field.description }}" > custom_templates/only_descriptions.jinja

settings-doc generate \
 --class src.settings.AppSettings \
 --output-format only_descriptions \
 --templates custom_templates
```

## Custom settings attributes in templates

By default, there are several variables available in all templates:
- `heading_offset` - the value of the `--heading-offset` option. Defaults to `0`.
- `fields` is a list of `str` / [`FieldInfo`](https://github.com/samuelcolvin/pydantic/blob/master/pydantic/fields.py) tuples. The string is the name of the settings attribute and the values come from `BaseSettings.model_fields.values()`. In other words, a list of individual settings fields and their names. If multiple classes are used to generate the documentation, `FieldInfo`s from all classes are collected into `fields`. The information about original classes is not retained.
- `classes` - a dictionary, where keys are the `BaseSettings` sub-classes and values are lists of extracted `FieldInfo`s of that class. This can be used for example to split individual classes into sections.

Extra parameters unknown to pydantic can be stored as a dict in the `json_schema_extra` attribute.

To access information from the `BaseSettings` classes, use the `classes` variable in the templates:

```jinja2
{% for cls, fields in classes.items() %}
# {{ cls.__name__ }}
{% endfor %}
```

## As a pre-commit hook

It's possible to use `settings-doc` as a pre-commit hook to keep your documentation up to date. There is one hook `id` per output format:
- `settings-doc-markdown`
- `settings-doc-dotenv`

There are two caveats:

1. You have to provide *all* the arguments (except `--output-format`) in the `args` section.
2. You have to provide `additional_dependencies`, specifying each package, that is imported in
your module. For example, if you use YAML loading for your settings, and you have `import yaml` in
your module, you have to specify it. Depending on how your imports are organized, you might need to
specify *all* of your dependencies.

Example `.pre-commit-config.yaml` section provided below:

```yaml
- repo: https://github.com/radeklat/settings-doc
  rev: '3.0.0'
  hooks:
    - id: settings-doc-markdown
      args:
        - '--module'
        - 'src.settings'
        - '--update'
        - 'README.md'
        - '--between'
        - "<!-- generated env. vars. start -->"
        - "<!-- generated env. vars. end -->"
        - '--heading-offset'
        - '1'
      additional_dependencies:
        - "pyyaml>=5.3.1"
```

You can use the same hook to check if the documentation is up-to-date in CI:

```shell
pip install pre-commit
pre-commit run --all-files settings-doc-markdown  # or other settings-doc-<output-format>
```

Consider caching the `~/.cache/pre-commit` environment cache for faster subsequent runs.

# Features overview

- Output into several formats with `--output-format`: markdown, dotenv
- Writes into stdout by default, which allows piping to other tools for further processing.
- Able to update specified file with `--update`, optionally between two given string marks with `--between`. Useful for keeping documentation up to date.
- Additional templates and default template overrides via `--templates`.

## Markdown

- Allows setting a `--heading-offset` to fit into existing documentation.
- Intelligently formats example values as:
  - Single line if all values fit within 75 characters.
  - List of values if all values won't fit on a single line.
  - List of `<VALUE>: <DESCRIPTION>` if example values are tuples of 1-2 items.

## .env

- Leaves environment variables commented if they have a default value as the app doesn't require them.
