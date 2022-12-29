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
- Option to use all sub-classes of `pydantic.BaseSettings` inside a module with a new `--module` option.

## [0.5.1] - 2021-11-12

### Fixes

- Updating document when the content hasn't changed no longer fails.

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

[Unreleased]: https://github.com/radeklat/settings-doc/compare/1.0.0...HEAD
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