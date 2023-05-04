# Contribution

> Work in progress

- usage of Datatypes of TVL

# Extend the TSL

Primitives and processing styles are defined in YAML files.
The generator uses those files to generate the code for the TSL.


The following sections describe how to add new primitives and processing styles.


- where to find config files -> primitive_data
- structure of config files


## Add a new primitive


### Primitive classes

The TSL Generator project contains a subproject called _primitive_data_.
This subproject contains the YAML files, which define the primitives and processing styles.
The primitives are grouped into classes.
Each class is defined in a separate YAML file in the subfolder _primitives_.
For example the _calc_ class contains all arithmetic primitives with element wise operations.

Each class file begins with a header (the first yaml document, see [YAML Documents](https://www.yaml.info/learn/document.html) for more info), which contains the name of the class and the description of the class.
The following documents contain a list of primitives.

### Primitive declaration

- How to declare a new primitive
  - needed parameters in YAML file
  - optional parameters in YAML file
  - Testing ???

### Primitive implementation

- How to implement a new primitive
  - needed parameters in YAML file
  - optional parameters in YAML file



## Add a new vector extension

- config files
- How to implement a new vector extension
  - needed parameters in YAML file
  - optional parameters in YAML file
