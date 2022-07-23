# Exammple Channel
The Example channel is an educational channel meant to showcase the ability to add 3D boxes to a warehouse model and render images with annotations. 


## Graph Requirements
The following nodes are required to be put in every graph to have the channel run as intended:
- Random Placement: 
- Render: 

## Channel Nodes
The following nodes are available in the channel:
| Name | Inputs | Outputs | Description |
|---|---|---|---|
| Render | Objects<br />Width (px)<br />Heigth (px) |  | The final node in the graph that is used to render the scene, generating the image and annotation outputs. |
| Warehouse | Warehouse Generator | This node generates the warehouse in which the boxes will be randomly placed. |
| Random Placement | Object Generators<br />Number of Objects | Objects | This node randomly determines where to place the box objects. |
| Box1 |  | Box1 Generator | Generates a box. |