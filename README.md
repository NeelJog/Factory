# Example Channel
The Factory channel is a Rendered.ai-developed channel that is used to help users learn some of the basics around channel development. In this channel we showcase a Blender-based scene with boxes randomly placed in a warehouse.


## Setup
[Setting up the Development Environment](https://support.rendered.ai/dg/Setting-Up-the-Development-Environment.1576501249.html):
Rendered.ai provides Development Docker Images that can be used with VSCode to simplify setting up your environment for channel development and can also accelerate the channel deployment process. Rendered.ai provides a number of public docker images that include Blender for CPU and GPU-based channels. To see a full list of images, visit Rendered.ai's [ECR Public Gallery site](https://gallery.ecr.aws/renderedai/).


## Running Locally
To run a graph from this channel, you'll need to locally mount the volumes using the 'anamount' command. The volumeIds required for this channel to run are:
- ee6968eb-5391-436c-8662-3818f559bf64
You'll need to create a Rendered.ai account and sign in to access this volume. If you sign in and still don't have permissions to access the volume, contact admin@rendered.ai for help.

The following commands will mount the required volumes then execute the default graph.
```bash
anamount --channel factory.yml
ana --channel factory.yml --graph graphs/default.yml
```


## Documentation
Documentation has been created for this channel in the docs/ directory. This includes information about graph requirements for the channel, available nodes and other channel-related insights.


## Graphs
The available graphs for the channel are located in the graphs/ directory.

| graph | description |
|---|---|
| default.yml | Randomly places boxes in the Warehouse |


## Mappings
The available mappings for the channel are located in the mappings/ directory.

| mapping | description |
|---|---|
| default.yml | All objects in the channel are categorized into a unique class. |
