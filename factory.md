# factory Channel
*Description of the channel.*

## Graph Requirements
*Describe any requirements needed for running a graph, for example nodes that need to be connected in a certain order.*

## Channel Nodes
The following nodes are available in the channel:
| Name | Inputs | Outputs | Description |
|---|---|---|---|
| Box1 | - | Box1 Generator | Box1 for factory |
| Warehouse | - | Warehouse Generator | - |
| Random Placement | Object Generators<br />Number of Objects<br />Warehouse Generator | Objects | Place objects in a scene |
| Render | Objects<br />Camera<br />Light Intensity<br />Width (px)<br />Height (px)<br />Calculate Obstruction | - | Render and image for the scene and create associated annotations and metadata |
| Weight | Generator<br />Weight | Generator | Change the weight of a generator |
| Random Integer | low<br />high<br />size | out | Generate random integers from low (inclusive) to high (exclusive), see numpy.random.randint for details |
