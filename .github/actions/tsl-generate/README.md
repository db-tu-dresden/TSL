# TSL Generator action

This action runs the docker container based on the image `docker://jpietrzyktud/tsl_generator:latest` and generates a specific version of the TSL.

## Inputs

### `targets`: string

**Required**  Comma separated list of targets to generate, e.g., 'sse,sse2,sse4_1'.

## Outputs

### `name`: string

**Required** Name of the generated files.
  
### `out`: string

**Required** Path to the generated files.
  
### `msg`: string

**Required** Verbose message from the action.

### `success`:

**Required** Whether the action was successful (1, 0 otherwise).

## Example usage

    - name: TSL Generate
      id: generate
      uses: ./.github/actions/tsl-generate
      with:
        image: ${{ vars.GENERATION_TAG }}
        targets: ${{ matrix.target_flags }}