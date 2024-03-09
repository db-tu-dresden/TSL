# Debian package (*.deb) builder action

This action runs the docker container based on the image `docker://jpietrzyktud/tsl_package_deb:latest` and builds a debian package for libtsl-dev.

## Inputs

### `tag`: string

**Required**  The current tag.

### `tsl`: string

**Required**  Path to the hollistic TSL tarball.

### `prefix`: string

**Required**  Prefix of directories in the tarball.

## Outputs

### `name`: string

**Required** Name of the generated deb file.
  
### `out`: string

**Required** Path to the generated files.
  
### `msg`: string

**Required** Verbose message from the action.

### `success`:

**Required** Whether the action was successful (1, 0 otherwise).

## Example usage

    - name: Create DEB Package
      id: deb
      uses: ./.github/actions/tsl-deb-build
      with:
        tag: ${{ inputs.tag-name }}
        tsl: tsl.tar.gz
        prefix: tsl/generate_tsl_