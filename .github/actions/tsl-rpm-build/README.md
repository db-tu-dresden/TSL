# RPM package (*.rpm) builder action

This action runs the docker container based on the image `docker://jpietrzyktud/tsl_package_rpm:latest` and builds a rpm package for libtsl-dev.

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

    - name: Create RPM Package
      id: deb
      uses: ./.github/actions/tsl-rpm-build
      with:
        tag: ${{ inputs.tag-name }}
        tsl: tsl.tar.gz
        prefix: tsl/generate_tsl_