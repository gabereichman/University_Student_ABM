from model import UniversityRevenue
from mesa.visualization import Slider, SolaraViz, make_space_component, make_plot_component
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
        value=1000,
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
        value=0.3,
        min=0.1,
        max=1,
        step=0.1
    ),
    "merit_window": Slider(
        label="Wealth-Merit Independence",
        value=1,
        min=0,
        max=1,
        step=0.1
    ),
    "incentive": Slider(
        label="Revenue Incentive Weight",
        value=1,
        min=0,
        max=1,
        step=0.1
    ),
    "information": {
        "type": "Select",
        "value": "No information",
        "values": ["No information", "Partial information", "Perfect information"],
        "label": "Student Financial Information"
    }
}

model = UniversityRevenue()

page = SolaraViz(
    model,
    components=[
        # Vizualize the model itself
        make_space_component(agent_portrayal=agent_portrayal, backend="matplotlib"),
        # Vizualize merit and wealth stratification together
        make_plot_component(["Merit_std", "Wealth_std"]),

        make_plot_component(["Tuition_Prestige_Corr"]),

        make_plot_component(["Total_Revenue"])

        ],
    model_params=model_params,
    name="University Revenue Model",
)
page
