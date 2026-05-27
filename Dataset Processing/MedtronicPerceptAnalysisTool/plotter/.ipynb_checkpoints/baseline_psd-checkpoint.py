import matplotlib.pyplot as plt
from matplotlib.figure import Figure

def plot_baseline_psd_of_each_channel(pt_data_obj):
    def plot_baseline_psd_with_baseline_dict(baseline_dict:dict) -> Figure:
        nrows, ncols, inches, xyratio = 1, 2, 3, 2
        fig, axs = plt.subplots(nrows, ncols, figsize=(ncols*inches*xyratio, nrows*inches), sharex=True, sharey=True)

        for (key, value) in baseline_dict.items():
            
            if "left" in key.lower(): ax = axs[0]
            if "right" in key.lower(): ax = axs[1]

            ax.set_title(f"Baseline PSD for {key}")
            ax.set_ylabel("PSD")
            ax.set_xlabel("Freq (Hz)")
            
            x = value[0]
            y = value[1]
            ax.scatter(x, y, label=key, marker='.', s=2, color='red')
            ax.plot(x, y, alpha=0.3, color='grey')

        return fig

    baseline_dict = pt_data_obj.get_baseline_dict()
    fig = plot_baseline_psd_with_baseline_dict(baseline_dict=baseline_dict)

    patient_prefix = "-".join(pt_data_obj.__class__.__name__.split("_")[:2])
    fig.suptitle(f"{patient_prefix} - Baseline PSD for each channel")

    fig.set_layout_engine("constrained")

    return fig