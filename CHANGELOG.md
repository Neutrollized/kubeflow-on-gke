# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## [0.3.1] - 2026-04-16
### Changed
- Increased some `kubectl wait` timeout values

## [0.3.0] - 2026-04-14
### Added
- Taskfile task for setting up Pipelines v1 (unused)
- Taskfile task to run `kustomize edit fix` recursively
- `examples/requirements.txt`
- `examples/hello_world_experiment.py`
### Fixed
- Missing Pipeline CRDs (used by Pipelines v2)

## [0.2.0] - 2026-04-13
### Added
- Single-command install instructions added to README
### Removed
- `common/cert-manager/base` install
### Fixed
- Status check for Dex install task

## [0.1.0] - 2026-04-12
### Added
- Initial commit
