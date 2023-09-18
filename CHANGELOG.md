# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).
Types of changes are:

- **Breaking changes** for breaking changes.
- **Features** for new features or changes in existing functionality.
- **Fixes** for any bug fixes.
- **Deprecated** for soon-to-be removed features.

## [Unreleased]

## [3.0.0] - 2023-09-19

### Breaking changes

Upgrade to `pydantic` 2.x. If you need to use pydantic 1.x, please use the `2.x` release of `settings-doc`. New features will be available only in `settings-doc` 3.x and later, unless a backport is requested.

The upgrade changes couple of things in the `pydantic` library that also need to be reflected in the templates:
- `pydantic.BaseSettings` is now `pydantic_settings.BaseSettings`
- `pydantic.Field` no longer accepts arbitrary `**kwargs`. This has several implications for the Jinja2 templates:
    - `field.field_info` is no longer available. All the attributes have moved to the `field` object itself. For example `field.field_info.description` is now `field.description`.
    - `json_schema_extra` must be passed as a keyword argument and contain a dictionary. This is then available in the Jinja2 templates as `field.json_schema_extra` instead of the previous `field.field_info.extra`.

- The type of the field exposed to templates changed from `ModelField` to `FieldInfo`. This means that:
  - `FieldInfo` no longer contain the name of the settings key. Therefore, `fields` has been changed to `list[tuple[str, FieldInfo]]` (instead of `list[ModelField]`), where the `str` value is name of the settings key. To iterate over the fields, use `for env_name, field in fields` instead of `for field in fields`.
  - `ModelField.type_` has changed to `FieldInfo.annotation`.
  - `ModelField.required` has changed to `FieldInfo.is_required()`.
  - `ModelField.default is not None` has changed to `FieldInfo.default is not pydantic_core.PydanticUndefined`. A new helper function `has_default_value(field)` has been added to the templates to make this easier to check.
  - Check if `FieldInfo` type is `typing.Literal` has been abstracted into helper function `is_typing_literal`. The check is different for Python 3.8 and for later versions of Python.

## [2.1.0] - 2023-09-16

### Features

- Add [support for `pre-commit` hooks](README.md#as-a-pre-commit-hook).

## [2.0.0] - 2023-06-25

### Breaking changes

- Drops Python 3.7 support.

## [1.0.0] - 2022-12-29

### Features

- Add support for Python 3.11.

### Fixes

- Dependencies update.

## [0.8.1] - 2022-02-02

### Fixes

- Missing space before headings in Markdown template.

## [0.8.0] - 2022-01-25

### Features

- `classes` of type `Dict[Type[BaseSettings], List[ModelField]]` exposed to templates.

## [0.7.0] - 2021-11-26

### Breaking changes

- Removed support for Python 3.6.
- Removed `tasks` folder, in favour of `delfino`.

## [0.6.1] - 2021-11-17

### Fixes

- Removed unused dependency on `termcolor`.

## [0.6.0] - 2021-11-17

### Features

- The `--class` option can be specified more than once and is also optional.
- Option to use all subclasses of `pydantic.BaseSettings` inside a module with a new `--module` option.

## [0.5.1] - 2021-11-12

### Fixes

- Updating document when the content hasn't changed, no longer fails.

## [0.5.0] - 2021-11-12

### Features

- Remove top level heading from the Markdown template.

### Fixes

- Description of `generate --templates`.

## [0.4.0] - 2021-11-11

### Breaking changes

- All existing options moved in the `generate` sub-command.

### Features

- New sub-command `templates` for copying templates into selected folder.

## [0.3.0] - 2021-11-10

### Breaking changes

- Project renamed to `settings-doc`

## [0.2.0] - 2021-11-09

### Features

- Option `--update` to overwrite an existing file.
- Option `--between` to update only a portion of a file specified by `--update`, between two given marks.

## [0.1.1] - 2021-11-07

### Fixes

Add classifiers to the package.

## [0.1.0] - 2021-11-05

- Initial release

[Unreleased]: https://github.com/radeklat/settings-doc/compare/3.0.0...HEAD
[3.0.0]: https://github.com/radeklat/settings-doc/compare/2.1.0...3.0.0
[2.1.0]: https://github.com/radeklat/settings-doc/compare/2.0.0...2.1.0
[2.0.0]: https://github.com/radeklat/settings-doc/compare/1.0.0...2.0.0
[1.0.0]: https://github.com/radeklat/settings-doc/compare/0.8.1...1.0.0
[0.8.1]: https://github.com/radeklat/settings-doc/compare/0.8.0...0.8.1
[0.8.0]: https://github.com/radeklat/settings-doc/compare/0.7.0...0.8.0
[0.7.0]: https://github.com/radeklat/settings-doc/compare/0.6.1...0.7.0
[0.6.1]: https://github.com/radeklat/settings-doc/compare/0.6.0...0.6.1
[0.6.0]: https://github.com/radeklat/settings-doc/compare/0.5.1...0.6.0
[0.5.1]: https://github.com/radeklat/settings-doc/compare/0.5.0...0.5.1
[0.5.0]: https://github.com/radeklat/settings-doc/compare/0.4.0...0.5.0
[0.4.0]: https://github.com/radeklat/settings-doc/compare/0.3.0...0.4.0
[0.3.0]: https://github.com/radeklat/settings-doc/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/radeklat/settings-doc/compare/0.1.1...0.2.0
[0.1.1]: https://github.com/radeklat/settings-doc/compare/0.1.0...0.1.0
[0.1.0]: https://github.com/radeklat/settings-doc/compare/initial...0.1.0