# from MedtronicPerceptAnalysisTool.plotter import plot_updrs_averages
from ...data_wrapper.base import Patient_Dataset_Base
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker
from ...utility import constants
from ..plotter import IndividualPlotter

# @IndividualPlotter.register
def plot_updrs_averages(pt_data_obj: Patient_Dataset_Base):
    
    df = pt_data_obj.get_dataframe_updrs(summary=True)
    # mask = df.apply(lambda row: pd.notna(row).all(), axis="columns")  # Filter rows with nan
    # df = df.loc[mask, :]
    treatment_order = df.columns.get_level_values(1).to_list()
    treatment_order_map = {key:value for key, value in zip(treatment_order, range(len(treatment_order)))}

    # Check number of rows without nan
    
    nrows, ncols, inches, xyratio = 1, 4, 5, 1
    fig, axs = plt.subplots(
        nrows,
        ncols, 
       figsize=(ncols*inches*xyratio, nrows*inches*xyratio),
       sharex='all', 
       sharey='all')
    
    for rowname, data in df.iterrows():
        
        if rowname in ["L", "R"]:
            ax = axs[0]
            ax.set_title(f"Left and Right body")
        elif rowname in ["LUE", "RUE"]:
            ax = axs[1]
            ax.set_title(f"Left and Right Upper Extremities (UE)")
        elif rowname in ["Body"]:
            ax = axs[2]
            ax.set_title("Body overall")
        elif rowname == "LipJaw":
            ax = axs[3]
            ax.set_title("Lip and Jaw")
        else:
            continue
            
        
        match rowname[0]:
            case "L":
                color=constants.COLOR_LEFT_HEMISPHERE
            case "R":
                color=constants.COLOR_RIGHT_HEMISPHERE
            case _:
                color="Green"
                
        y = data.values
        x = [treatment_order_map[index] for index in data.index.get_level_values(1)]
        ax.scatter(x, y, label=rowname, color=color)
        ax.plot(x, y, color=color, alpha=0.3)
        
    # Fix subplot formatting
    for ax in axs:
        ax.legend()
        ax.set_ylabel("Average UPDRS value")
        ax.set_ylim([-0.3, 5.3])
        ax.set_xlim([-0.1*len(treatment_order_map), 1.1*(len(treatment_order_map)-1)])
        
        ax.xaxis.set_major_locator(ticker.FixedLocator(list(treatment_order_map.values())))
        ax.xaxis.set_major_formatter(ticker.FixedFormatter(list(treatment_order_map.keys())))
    
    patient_prefix = "_".join(pt_data_obj.__class__.__name__.split("_")[:2])
    fig.suptitle(f"{patient_prefix} - Average UPDRS (grouped) - Glove on {pt_data_obj.glove_hand}")
    fig.set_layout_engine("constrained")
    return fig