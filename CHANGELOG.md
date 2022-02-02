# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).
Types of changes are:

- **Added** for new features.
- **Changed** for changes in existing functionality.
- **Deprecated** for soon-to-be removed features.
- **Removed** for now removed features.
- **Fixed** for any bug fixes.
- **Security** in case of vulnerabilities.

## [Unreleased]

## [0.8.1] - 2022-02-02

### Fixed

- Missing space before headings in Markdown template.

## [0.8.0] - 2022-01-25

### Added

- `classes` of type `Dict[Type[BaseSettings], List[ModelField]]` exposed to templates.

## [0.7.0] - 2021-11-26

### Removed

- Support for Python 3.6.
- `tasks` folder, in favour of `delfino`.

## [0.6.1] - 2021-11-17

### Fixed

- Removed unused dependency on `termcolor`.

## [0.6.0] - 2021-11-17

### Changed

- The `--class` option can be specified more than once and is also optional.

### Added

- An option to use all sub-classes of `pydantic.BaseSettings` inside a module with a new `--module` option.

## [0.5.1] - 2021-11-12

### Fixed

- Updating document when the content hasn't changed no longer fails.

## [0.5.0] - 2021-11-12

### Changed

- Remove top level heading from the Markdown template.

### Fixed

- Description of `generate --templates`.

## [0.4.0] - 2021-11-11

### Changed

- All existing options moved in the `generate` sub-command.

### Added

- New sub-command `templates` for copying templates into selected folder.

## [0.3.0] - 2021-11-10

### Changed

- Project renamed to `settings-doc`

## [0.2.0] - 2021-11-09

### Added

- Option `--update` to overwrite an existing file.
- Option `--between` to update only a portion of a file specified by `--update`, between two given marks.

## [0.1.1] - 2021-11-07

### Fixed

Add classifiers to the package.

## [0.1.0] - 2021-11-05

- Initial release

[Unreleased]: https://github.com/radeklat/settings-doc/compare/0.8.1...HEAD
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