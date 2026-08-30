# Product Requirements

## User outcome

Help a photographer find, understand, and manually prepare promising stock-image candidates from local folders without risking originals.

## Initial requirements

- Accept a local folder path only when explicitly chosen by the user.
- Recursively identify supported image file extensions.
- Report a deterministic inventory: relative path, filename, byte size, and modification time.
- Exclude non-image files and do not follow symlinks.
- Return information only; do not modify files, folders, or metadata.

## Safety and privacy

- Operate offline in the initial release.
- Never send paths, images, or metadata to a remote service.
- Do not store photos in the project workspace or GitHub repository.
- Future metadata and catalog storage must remain local and excluded from Git.
