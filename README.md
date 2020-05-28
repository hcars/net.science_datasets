# net.science_datasets
A repository of networks scraped from various researchers websites. These networks are to be incorporated into BII's net.science
cyber-infrastructure. 
# Organization 
## xxxxx_networks
Folders named xxxxx_networks contain two folders: edge_lists and node_id_mappings. The files in edge_lists are a graph in a
comma-separated edge list format. E.g. an edge from node 1 to node 2 is represented by 1,2,(weight if the graph is weighted). 
Each xxxxx_networks folders comes from a different website. The node_id_mappings contains a mapping in a CSV format between the node ids
contained in the edge_lists files and the node attributes if there are any.
## download_scripts
This is a collection of Python scripts which scrape networks from different sources.
