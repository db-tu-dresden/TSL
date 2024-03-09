# TSL build and test action for arm64 hardware

This action runs the docker container based on the image `docker://jpietrzyktud/tsl_build_and_test_arm:latest`, builds an already generated TSL and run tests.

## Inputs

### `compiler`: string

**Required**  Compiler that should be used (so far, only g++ is supported)

### `tsl`: string

**Required**  Path to the TSL top level.

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

    - name: TSL Build and Test
      uses: ./.github/actions/tsl-test-arm
      with:
        compiler: g++
        tsl: tsl/arm