import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
from graphviz import Digraph

# Error checking
outputs_dir = '../outputs'
os.makedirs(outputs_dir, exist_ok=True)


# Create a Digraph object
dot = Digraph(comment='CI/CD Pipeline Flowchart')

# Define graph aesthetics
dot.attr(rankdir='LR', size='10')

# Add nodes for the stages
stages = ['Build', 'Test', 'Release', 'Quality', 'Package', 'Images']
for stage in stages:
    dot.node(stage, shape='rectangle')

# Add nodes for specific jobs with conditions
dot.node('Workflow Rules', shape='diamond')
dot.node('Build FSW', shape='ellipse')
dot.node('Build Docs', shape='ellipse')
dot.node('Unit Tests', shape='ellipse')
dot.node('Acceptance Tests', shape='ellipse')
dot.node('Release', shape='ellipse', style='filled', fillcolor='lightgrey')
dot.node('Quality Checks', shape='ellipse')
dot.node('Package Petalinux', shape='ellipse')
dot.node('Build Docker Images', shape='ellipse')
dot.node('Build Board', shape='ellipse')

# Add edges to illustrate the flow
dot.edge('Workflow Rules', 'Build')
dot.edge('Build', 'Test')
dot.edge('Test', 'Release')
dot.edge('Build', 'Build FSW')
dot.edge('Build', 'Build Docs')
dot.edge('Test', 'Unit Tests')
dot.edge('Test', 'Acceptance Tests')
dot.edge('Release', 'Quality Checks')
dot.edge('Quality', 'Package')
dot.edge('Package', 'Package Petalinux')
dot.edge('Package Petalinux', 'Images')
dot.edge('Images', 'Build Docker Images')
dot.edge('Release', 'Build Board')

# Output the graph to a file and display it
dot.format = 'png'
output_path = os.path.join(outputs_dir, 'cicd_pipeline_flowchart')
dot.render(output_path, view=True)
