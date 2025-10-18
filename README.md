# TODO
- Feature engineering
- Model training/tuning
- Model evaluation

---

# Problem Statement
When responding to emergencies, every second counts. First responders need to be able to quickly get to the 
scene of an emergency.  This is where the EMS Predictor comes in.  This application will create a heatmap that 
shows the display areas that are at risk of being hit by an emergency. 


---
# Data
San Francisco: Fire Department and Emergency Medical Services Dispatched Calls for Service [Link to data website](https://data.sfgov.org/Public-Safety/Fire-Department-Calls-for-Service/nuek-vuh3).


---
# Environment Setting
```zsh
conda env create -f environment.yml
python -m ipykernel install --user --name ems-predictor --display-name "Python (ems-env)"
```
