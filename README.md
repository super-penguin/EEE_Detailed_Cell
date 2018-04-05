## Test glutamate evoked plateau potentials in a detailed model (CA229 cell)

### Updated on April. 05, 2018
    Both synaptic AMPARs/NMDARs and exsynaptic NMDARs are activated by one
    NetStim.
    Synaptic AMPARs/NMDARs get activated 10~100 ms after the stimulation.
    exsynaptic NMDARs get activated 15~115 ms after the stimulation.
    gmax for AMPA is 0.05nS; gmax for NMDA is 0.005nS.


### Files:
    1. Experiment_no_spines.py    
        - Code to add AMPA and NMDA receptors on basal[34]
        - It will generate figures and json files to store the voltage traces
        - Modify the parameters in "__main__" to choose the simulation

    2. CA229.py   - python class with all the cell membrane properties
            (the Geometry and 3d shape is defined in this python class as well
                --- for better usage in network or NetPyNE)

    3. compile.py     - compile all the mod files in folder: mod

    4. Analysis_for_trace_location.py   - Plot traces at different location on soma and basal dendrites

    5. Analysis_for_plateau_duration.py  - Generate data analysis files and figures

    6. analysis_utils.py   - analysis of plateau duration, ISI and number of spikes

    7. utils.py    - to save figures and simulation results in a folder with name of today's date


### Instruction:

    Compile mod files: python compile.py

    Add parameters for testing in "main" of Experiment_no_spines.py

        (change number pool1 of synaptic AMPARs and NMDARs;
        change number pool 2 of exsyantpic NMDARs;
        change Beta and Cdur of NMDARs;
        change of stimulation location;
        change of syanptic weights;)

    Run the file: python Experiment_no_spines.py

### Output:
    All the figures and json data will be saved in a different folder with name of today's date.
