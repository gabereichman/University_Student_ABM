from model import UniversityRevenue
from mesa.visualization import Slider, SolaraViz, make_space_component
from mesa.visualization.components import AgentPortrayalStyle

def agent_portrayal(agent):
    if agent.label == 'S':
        marker = 'o'
        color = (0, agent.merit, 0)
        size = 20
    else:
        marker = '*'
        color = (agent.prestige, 0, 0)
        size = 20
    

    return AgentPortrayalStyle(
        color = color,
        marker= marker,
        size= size,
    )
    
model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "student_count": Slider(
        label="Number of Students",
        value=100,
        min=10,
        max=1000,
        step=10,
    ),
    "university_count": Slider(
        label="Number of Universities",
        value=5,
        min=2,
        max=50,
        step=1,
    ),
    "donate": Slider(
        label="Donation proportion",
        value=0.5,
        min=0,
        max=10,
        step=0.1
    ),
    "capacity_prop": Slider(
        label="Capacity proportion",
        value=0.5,
        min=0.1,
        max=1,
        step=0.1
    ),
    "information": {
        "type": "Select",
        "value": "single",
        "values": ["No information", "Partial information", "Perfect information"],
        "label": "Student Financial Information"
    }
}

model = UniversityRevenue()

page = SolaraViz(
    model,
    components=[make_space_component(agent_portrayal=agent_portrayal, backend="matplotlib")],
    model_params=model_params,
    name="University Revenue Model",
)
page
# I still need to add data-collection visualizations