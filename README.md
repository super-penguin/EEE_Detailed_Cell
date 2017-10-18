## Test glutamate evoked plateau potentials in a detailed model (CA229 cell)

### Updated on Oct. 18, 2017
    Both synaptic AMPARs/NMDARs and exsynaptic NMDARs are activated by one
    NetStim.
    No randomness in receptor activation time yet.
    gmax for AMPA is 0.1nS; gmax for NMDA is 0.05nS.


### Files:
    1. Experiment_10_09.py    - Code to add AMPA and NMDA receptors

    2. CA229.hoc      - hoc file with the Geometry and 3d shape

    3. CA229_PFC.py   - python class with all the cell membrane properties (CA229.hoc will be loaded by this file)

    4. compile.py     - compile all the mod files in folder: mod

    5. Analysis_for_trace_location.py   - Plot traces at different location on soma and basal dendrites

    6. analysis_utils.py   - analysis of plateau duration, ISI and number of spikes

    7. utils.py    - to save figures and simulation results


### Instruction:

    Compile mod files: python compile.py

    Add parameters for testing in "main" of Experiment_10_09.py

        (change number pool1 of synaptic AMPARs and NMDARs;
        change the number pool 2 of exsyantpic NMDABRs;
        change Beta and Cdur of NMDARs)

    Run the file: python Experiment_10_09_14.py

### Output:
    All the data and folder will be saved in a different folder with name of today's date.
