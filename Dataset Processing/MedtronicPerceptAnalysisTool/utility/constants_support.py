# Ref: Fasano, A., Mure, H., Oyama, G., Murase, N., Witt, T., Higuchi, Y., 
#      Singer, A., Sannelli, C., & Morelli, N. (2024). Subthalamic nucleus local 
#      field potential stability in patients with Parkinson’s disease. Neurobiology 
#      of Disease, 199, 106589. 
#      https://doi.org/10.1016/j.nbd.2024.106589
BIOMARKER_BANDS_FASANO_2024 = {
    "alpha": (8, 12),
    "low-beta": (12, 20),
    "high-beta": (20, 30),
    "gamma": (30, 100),
}

# Ref: Yin, Z., Zhu, G., Zhao, B., Bai, Y., Jiang, Y., Neumann, W.-J., Kühn, 
#      A. A., & Zhang, J. (2021). Local field potentials in Parkinson’s disease: A 
#      frequency-based review. Neurobiology of Disease, 155, 105372. 
#      https://doi.org/10.1016/j.nbd.2021.105372
BIOMARKER_BANDS_YIN_2021 = {
    "delta": (0, 3),
    "theta": (4, 7),
    "alpha": (8, 12),
    "low-frequency": (4, 12),
    "tremor-frequency": (4, 8),
    "beta": (13, 35),
    "low-beta": (13, 20),
    "high-beta": (21, 35),
    "gamma": (31, 200),
    "low-gamma": (31, 45),
    # "HFO": (200, ),  # > 200Hz
    "slow-HFO": (200, 300),
    "fast-HFO": (300, 400),
}

# Ref: Pfeifer, K. J., Kromer, J. A., Cook, A. J., Hornbeck, T., Lim, E. A., 
#      Mortimer, B. J. P., Fogarty, A. S., Han, S. S., Dhall, R., Halpern, C. H., & 
#      Tass, P. A. (2020). Coordinated Reset Vibrotactile Stimulation Induces 
#      Sustained Cumulative Benefits in Parkinson’s Disease. Frontiers in 
#      Physiology, 12. https://www.frontiersin.org/articles/10.3389/fphys.2021.624317
BIOMARKER_BANDS_PFEIFER_2020 = {
    "delta": (2, 4),
    "theta": (5, 7),
    "alpha": (8, 12),
    "low-beta": (13, 16),
    "mid-beta": (17, 20),
    "high-beta": (21, 30),
    "gamma": (31, 50),
}

# Ref: Gilron, R., Little, S., Perrone, R., Wilt, R., de Hemptinne, C., 
#      Yaroshinsky, M. S., Racine, C. A., Wang, S. S., Ostrem, J. L., Larson, P. 
#      S., Wang, D. D., Galifianakis, N. B., Bledsoe, I. O., San Luciano, M., 
#      Dawes, H. E., Worrell, G. A., Kremen, V., Borton, D. A., Denison, T., & 
#      Starr, P. A. (2021). Long-term wireless streaming of neural recordings for 
#      circuit discovery and adaptive stimulation in individuals with Parkinson’s 
#      disease. Nature Biotechnology, 39(9), 1078–1085. 
#      https://doi.org/10.1038/s41587-021-00897-5
BIOMARKER_BANDS_GILRON_2021 = {
    "alpha": (8, 12), 
    "beta": (12, 30),
    "gamma": (50, 90),
}

COLOR_LEFT_HEMISPHERE="Blue"
COLOR_RIGHT_HEMISPHERE="Red"
COLOR_STAGE_DBS_OFF="lightslategray"
COLOR_STAGE_ALL_ON="steelblue"
COLOR_STAGE_RVS="salmon"
