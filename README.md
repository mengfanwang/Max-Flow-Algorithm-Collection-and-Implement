# Max-flow Algorithms Implementation by MATLAB
By [Mengfan Wang](https://www.linkedin.com/in/mengfan-wang-29735314a/).

Virginia Tech [Computational Bioinformatics and Bio-imaging Laboratory (CBIL)](https://www.cbil.ece.vt.edu/).

## Introduction
This is an open-source repository used for implementing different max-flow algorithms, especially for large-scale data problems. This repository contains two parts. One part is the dataset used for validating max-flow algorithms, which categorizes graphs by different properties. The max-flow and min-cut results of all graphs are obtained from `maxflow` function in Matlab with the Boykov-Kolmogorov algorithm. It also contains several programs used for generating dataset or validate algorithms. The other part is algorithms implemented. All algorithms should have the same input and output method. That is, all algorithms are the same if regarded as black boxes except the running time. The results of approximate algorithms may slightly different. All algorithms are coded by Matlab so that anyone can modify and make their contribution but should obey these rules. 

## Contents
#### <a href="#Dataset">Dataset</a>
* [Categories](#Categories)
* [Structure and Fields](#StructureandFields)
* [Running Time Database](#RunningTimeDatabase)
#### <a href="#Input">Input</a>
#### <a href="#Output">Output</a>
#### <a href="#Algorithms and Codes">Algorithms and Codes</a>
* [General Codes](#GeneralCodes)

## <a id="Dataset"/>Dataset</a>
[Dataset link](https://drive.google.com/drive/folders/1Pz6YEsJ8QHLzCbWa_5-ptssVO1PoRnSP?usp=sharing) is here.

Some of the graphs are from the following websites, institutes or organizations:

* [MaxFlow Revisited](http://ttic.uchicago.edu/~dbatra/research/mfcomp/#synthetic)
* [SNAP](https://snap.stanford.edu/biodata/index.html)

### <h3 id="Categories">Categories</h3>
#### 1. Undirected(1) or Directed(2) 
#### 2. Number of Edges
* (1) Planar graph (m <= 3n-6)
* (2) m = O(n) but not planar
* (3) m = O(n^2) or more
* (4) Complete graph
#### 3. Precision
* (1) Unit capacity
* (2) Integral capacity
* (3) Single float capacity
* (4) Double float capacity
#### 4. The Ratio of Capacity (U)
* (1) Constant
* (2) U = O(m)
* (3) U > O(m) or containing infinite capacity edges.
#### 5. Scale
* The number of vertices should be 10^x to 10^(x+1)-1. x changes from 2 to 7, and even more in the future.

**Some special graphs may be supplemented as new categories in the future.

### <h3 id="StructureandFields">Structure and Fields</h3>
Each graph should be saved as a Matlab structure. The structure should contain the following fields:
#### 1. Vertices
This is an n by 1 matrix. n is the number of vertices. Entries must be positive integers, but may not start from 1 and may not continuous. It contains the source and sink. The data type of entries can be `uint16` or `uint32` (even more in the future version), based on n.

For example,

`uint16([16,57,3,89])` is a valid `Vertices`.

`uint16([-2,1,2,3])` is an invalid `Vertices`.

`unit16([9999999,1,2,3])` is a valid `Vertices` but may cause error.

`unit16([9999999,1,2,65535])` is an invalid `Vertices` because of duplicated vertices.

#### 2. Edges

This is an m by 2 matrix. m is the number of edges. Entries must be positive integers and appear in `Vertices`. The data type of entries should be the same as those in `Vertices`. If the graph is directed, the entries in the first column are the vertices which edges are oriented away from, and the entries in the second column are the vertices which edges are oriented towards. Multiple edges and loops may appear. Entries in `Vertices` may not appear.

#### 3. Capacities

This is an m by 1 matrix. Entries must be non-negative. Every entry represents the capacity of the edge which at the same position in `Edges`. If the graph has unit capacities, `Capacities` is an all 1 matrix. The data type can be `uint`, `single` or `double`.   

#### 4. Source
A positive integer, which represents the source of the graph. Its data type should be the same as the entries in `Vertices`.

#### 5. Sink
Similarly to `Source`, it represents the sink of the graph.

#### 6. MaxValue
An integer, or a single or double number, which is decided by the property of the graph. The data type is `single` or `double` even it's an integer. It represents the sum value of all max-flows after implementing a max-flow algorithm.

#### 7. MaxFlows
An m by 1 matrix. The data type is the same as `MaxValue`, but it may contain non-integer entries when `Capacities` is `uint` and `MaxValue` is integral.  Every entry represents the max-flow of the edge which at the same position in `Edges` after implementing a max-flow algorithm.

#### 8. SourceCut
A s by 1 matrix, representing a set of vertices connected to the source after implementing a min-cut algorithm.

#### 9. SinkCut
A t by 1 matrix, representing a set of vertices connected to the sink after implementing a min-cut algorithm. s+t=n.

#### 10. Flag
A 5-digital number. Each number represents the corresponding property in the former part `Categories` in order. When this part is modified, all graphs in the dataset will be modified.

For example, a 10000-vertices GTW graph's flag is 22334. Because it's directed, m=O(n) but not planar, single float capacity, and have 10^4 vertices with infinite capacity edges.

#### 11. Note
Any unfixed-length string or empty. Any comments or explanation can be appended here.


### <h3 id="RunningTimeDatabase">Running Time Database</h3>
A database is used for recording the running time. It's just a reference because the running time can change when using different algorithms and devices. However, for the same algorithm, the ratio of the running times of any two graphs should be almost constant. 

## <a id="Input"/>Input</a>
All inputs of all algorithms are the same. They are similar to the corresponding fields in the structure. Besides, there are some other properties or requirements.
#### 1. Vertices
 If the input data is not the integral type, it will be changed to `uint16` or `uint32`, based on the maximum entry. The algorithms should report an error if meeting the following cases:

* Invalid input: The input is not a one-column matrix with at least two entries.
* Invalid entries: Input contains zero, negative integers, non-integral numbers, or too large integers (>2^32). The last case may be removed in the future version.
* Duplicated vertices: Some entries appear more than one time.

#### 2. Edges
 If the input data is not the integral type, it will be changed to `uint16` or `uint32`, the same as the data type of entries in `Vertices`. The algorithms should report an error if meeting the following cases:

* Invalid input: The input is not a two-columns matrix.
* Invalid entries: Input contains zero, negative integers, non-integral numbers, or existing integers too large (>2^32). The last case may be removed in the future version.
* Invalid edges: Existing edges whose ends don't appear in `Vertices`.

The algorithms should report a warning if meeting the following cases:

* Multiple edges: Some edges appear more than one time.

#### 3. Capacities
 The algorithms should report an error if meeting the following cases:

* Invalid input: The input is not an m by 1 matrix. m is decided by `Edges`.
* Invalid capacities: Input contains negative entries.

#### 4. Source
If the input data is not the integral type, it will be changed to `uint16` or `uint32`, the same as the data type of entries in `Vertices`. The algorithms should report an error if meeting the following cases:

* Invalid input: The input is not a positive integer or too large (>2^32), or doesn't exist in `Vertices`.
* Same s&t: Source and sink are the same vertices.

#### 5. Sink
The same as `Source`.

#### 6. Calculation Method
There are three choices:`common`,`parallel`, and `gpu`. The default method is `common`. `common` means using a single core of CPU to run the algorithm. `parallel` means using different CPU cores for parallel computation. `GPU` means using GPU to accelerate calculation. The algorithms should report a warning and use the default `common` method if meeting the following cases:

* Invalid input: The input is not the same as any one of the three choices.
* Unsupported method: Input method is not supported by the algorithm.

#### 7. Data Precision
There are three choices:`int`,`single`, and `double`. The default method is `single`. Each choice means the data type of the input `Capacities` and the output `MaxValue` and `MaxFlows`. The algorithms should report a warning and use the default `single` method if meeting the following cases:

* Invalid input: The input is not the same as any one of the three choices.

The algorithms should report a warning and use the input method if meeting the following cases:

* Precision loss: The data type of `Capacities` is `double` but the input method is `single` or `int`, or the data type of `Capacities` is `single` but the input method is `int`.
* More time required: The data type of `Capacities` is `int` but the input method is `single` or `double`, or the data type of `Capacities` is `single` but the input method is `double`.


## <a id="Output"/>Output</a>
Outputs are similar to the corresponding fields in the structure.

#### 1. MaxValue
This output is gotten by calculating the sum of `MaxFlows`. This output of all algorithms should be the same, or very slightly different. If all capacities are integers or infinity, `MaxValue` should be an integer or infinity. 

#### 2. MaxFlows
This output of all algorithms should usually be the same or very slightly different, but may not because the optimal solutions may not unique. If all capacities are integers or infinity, `MaxFlows` may not be integral. The order is the same as the input `Edges`.

#### 3. SourceCut
Entries of this output of all algorithms should be the same if `MaxFlows` is the same, but the order is not required. If a max-flow algorithm doesn't provide a corresponding min-cut solution, this output may not be provided with a prompt message.

#### 4. SinkCut
The same as `SourceCut`.

## <a id="Algorithms and Codes"/>Algorithms and Codes</a>
### <h3 id="GeneralCodes">General Codes</h3>

* `inputCheck.m` For checking the input is valid or not.
* `graphGenerator.m` For generating graphs according to some requirements.
* `validation.m` For validating the result of an algorithm is correct or not.


Continued.