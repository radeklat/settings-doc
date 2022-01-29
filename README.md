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
    <img alt="Maintenance" src="https://img.shields.io/maintenance/yes/2022">
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
</p>

The same way you are able to generate OpenAPI documentation from [`pydantic.BaseModel`](https://pydantic-docs.helpmanual.io/usage/models/), `settings-doc` allows you to generate documentation from [`pydantic.BaseSettings`](https://pydantic-docs.helpmanual.io/usage/settings).

It is powered by the [Jinja2](https://jinja.palletsprojects.com/en/latest/) templating engine and [Typer](https://typer.tiangolo.com/) framework. If you don't like the built-in templates, you can easily modify them or write completely custom ones. All attributes of the [`BaseSettings`](https://pydantic-docs.helpmanual.io/usage/settings) models are exposed to the templates.

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

Let's assume the following [`BaseSettings`](https://pydantic-docs.helpmanual.io/usage/settings) in `src/settings.py` of a project:

```python
from pydantic import BaseSettings

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
from pydantic import BaseSettings, Field

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

echo "{{ field.title }}" > custom_templates/only_titles.jinja

settings-doc generate \
 --class src.settings.AppSettings \
 --output-format only_titles \
 --templates custom_templates
```

## Custom settings attributes in templates

By default, there are several variables available in all templates:
- `heading_offset` - the value of the `--heading-offset` option. Defaults to `0`.
- `fields` the value of `BaseSettings.__fields__.values()`. In other words, a list of individual settings fields. Each field is then an instance of [`ModelField`](https://github.com/samuelcolvin/pydantic/blob/master/pydantic/fields.py). If multiple classes are used to generate the documentation, `ModelField`s from all classes are collected into `fields`. The information about original classes is not retained.
- `classes` - a dictionary, where keys are the `BaseSettings` sub-classes and values are lists of extracted `ModelField`s of that class. This can be used for example to split individual classes into sections.

Extra parameters unknown to pydantic are stored in `field.field_info.extra`. Examples of such parameters are `example` and `possible_values`.

Even the bare `ModelField` without any extra parameters has a large number of attributes. To see them all, run this `settings-doc` with `--format debug`.

To access information from the `BaseSettings` classes, use the `classes` variable in the templates:

```jinja2
{% for cls, fields in classes.items() %}
# {{ cls.__name__ }}
{% endfor %}
```

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
