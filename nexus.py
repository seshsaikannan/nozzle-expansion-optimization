# ============================================================
# NEXUS 3.0 - ROCKET NOZZLE SIMULATION
# Version 2: Enhanced Performance Analysis and Validation
#
# Research:
# Computational Investigation of Rocket Nozzle Expansion
# Ratio Effects on Propulsive Performance Across
# Variable Atmospheric Conditions
#
# ============================================================


# ------------------------------------------------------------
# 1. IMPORT LIBRARIES
# ------------------------------------------------------------

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.optimize import brentq

# ------------------------------------------------------------
# Compatibility: lets the script run outside Google Colab/Jupyter
# ------------------------------------------------------------

try:
    display  # available in Jupyter / Colab
except NameError:
    def display(obj):
        print(obj)

print("=" * 60)
print("NEXUS 3.0 - ROCKET NOZZLE SIMULATION")
print("Version 2 - Enhanced Performance Analysis")
print("=" * 60)

print("Computational environment initialised.")


# ------------------------------------------------------------
# 2. BASELINE ROCKET ENGINE PARAMETERS
# ------------------------------------------------------------

Pc = 5.0e6          # Chamber pressure (Pa)
Tc = 3500.0         # Chamber temperature (K)
gamma = 1.22        # Specific heat ratio
R = 355.0           # Specific gas constant (J/kg K)
At = 0.01           # Throat area (m^2)
g0 = 9.80665        # Standard gravitational acceleration (m/s^2)


# Nozzle expansion ratios

expansion_ratios = [5, 10, 20, 40, 60, 80]


# Ambient pressures (Pa)

ambient_pressures = [
    101325,
    50000,
    20000,
    5000,
    1000,
    100
]


print("\nEngine parameters loaded successfully.")


# ------------------------------------------------------------
# 3. AREA-MACH RELATION
# ------------------------------------------------------------

def area_mach(M, gamma):

    term1 = 1 / M

    term2 = (
        (2 / (gamma + 1)) *
        (1 + ((gamma - 1) / 2) * M**2)
    )

    exponent = (gamma + 1) / (2 * (gamma - 1))

    return term1 * term2**exponent


# ------------------------------------------------------------
# 4. CALCULATE EXIT MACH NUMBER
# ------------------------------------------------------------

def calculate_exit_mach(expansion_ratio, gamma):

    def equation(M):

        return area_mach(M, gamma) - expansion_ratio

    # Select the supersonic solution

    Me = brentq(
        equation,
        1.000001,
        50
    )

    return Me


# ------------------------------------------------------------
# 5. CALCULATE EXIT PRESSURE AND TEMPERATURE
# ------------------------------------------------------------

def calculate_exit_conditions(Me, Pc, Tc, gamma):

    temperature_ratio = (
        1 + ((gamma - 1) / 2) * Me**2
    )

    Te = Tc / temperature_ratio

    Pe = Pc * temperature_ratio**(
        -gamma / (gamma - 1)
    )

    return Pe, Te


# ------------------------------------------------------------
# 6. CALCULATE MASS FLOW RATE
# ------------------------------------------------------------

def calculate_mass_flow(Pc, Tc, At, gamma, R):

    term1 = At * Pc

    term2 = np.sqrt(gamma / (R * Tc))

    term3 = (
        2 / (gamma + 1)
    )**(
        (gamma + 1) / (2 * (gamma - 1))
    )

    mdot = term1 * term2 * term3

    return mdot


# ------------------------------------------------------------
# 7. CALCULATE EXIT VELOCITY
# ------------------------------------------------------------

def calculate_exit_velocity(Me, Te, gamma, R):

    speed_of_sound = np.sqrt(gamma * R * Te)

    Ve = Me * speed_of_sound

    return Ve


# ------------------------------------------------------------
# 8. CALCULATE COMPLETE NOZZLE PERFORMANCE
# ------------------------------------------------------------

def calculate_performance(
    epsilon, Pa, Pc, Tc, At, gamma, R
):

    # Calculate exit Mach number

    Me = calculate_exit_mach(
        epsilon,
        gamma
    )

    # Calculate exit pressure and temperature

    Pe, Te = calculate_exit_conditions(
        Me,
        Pc,
        Tc,
        gamma
    )

    # Calculate exhaust velocity

    Ve = calculate_exit_velocity(
        Me,
        Te,
        gamma,
        R
    )

    # Calculate mass flow rate

    mdot = calculate_mass_flow(
        Pc,
        Tc,
        At,
        gamma,
        R
    )

    # Calculate exit area

    Ae = epsilon * At

    # Calculate individual thrust contributions

    momentum_thrust = mdot * Ve

    pressure_thrust = (Pe - Pa) * Ae

    # Calculate total thrust

    thrust = momentum_thrust + pressure_thrust

    # Calculate specific impulse

    Isp = thrust / (mdot * g0)

    # Classify exit-pressure condition

    if np.isclose(Pe, Pa, rtol=1e-6):

        flow_regime = "Ideally expanded"

    elif Pe > Pa:

        flow_regime = "Underexpanded"

    else:

        flow_regime = "Overexpanded"

    return {

        "Expansion_Ratio": epsilon,

        "Ambient_Pressure_Pa": Pa,

        "Exit_Area_m2": Ae,

        "Exit_Mach": Me,

        "Exit_Pressure_Pa": Pe,

        "Exit_Temperature_K": Te,

        "Exit_Velocity_m_s": Ve,

        "Mass_Flow_kg_s": mdot,

        "Momentum_Thrust_N": momentum_thrust,

        "Pressure_Thrust_N": pressure_thrust,

        "Thrust_N": thrust,

        "Specific_Impulse_s": Isp,

        "Flow_Regime": flow_regime
    }


# ------------------------------------------------------------
# 9. FULL SIMULATION MATRIX
# ------------------------------------------------------------

results = []

for epsilon in expansion_ratios:

    for Pa in ambient_pressures:

        result = calculate_performance(
            epsilon,
            Pa,
            Pc,
            Tc,
            At,
            gamma,
            R
        )

        results.append(result)


# Convert results into DataFrame

df = pd.DataFrame(results)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

print("\n" + "=" * 60)
print("SIMULATION RESULTS")
print("=" * 60)

print("Total simulation cases:", len(df))

display(df.round(4))


# ------------------------------------------------------------
# 10. EXPORT SIMULATION DATA
# ------------------------------------------------------------

df.to_csv(
    "NEXUS_V2_Simulation_Data.csv",
    index=False
)

print("\nSimulation dataset exported successfully.")


# ------------------------------------------------------------
# 11. GRAPH 1: EXIT MACH VS EXPANSION RATIO
# ------------------------------------------------------------

mach_results = []

for epsilon in expansion_ratios:

    Me = calculate_exit_mach(
        epsilon,
        gamma
    )

    mach_results.append(Me)


plt.figure(figsize=(9, 5))

plt.plot(
    expansion_ratios,
    mach_results,
    marker="o"
)

plt.xlabel("Nozzle Expansion Ratio")
plt.ylabel("Exit Mach Number")

plt.title(
    "Exit Mach Number vs Nozzle Expansion Ratio"
)

plt.grid(True)
plt.tight_layout()

plt.savefig(
    "NEXUS_V2_Exit_Mach.png",
    dpi=300
)

plt.show()


# ------------------------------------------------------------
# 12. GRAPH 2: THRUST VS AMBIENT PRESSURE
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

for epsilon in expansion_ratios:

    subset = df[
        df["Expansion_Ratio"] == epsilon
    ].sort_values("Ambient_Pressure_Pa")

    plt.plot(
        subset["Ambient_Pressure_Pa"] / 1000,
        subset["Thrust_N"] / 1000,
        marker="o",
        label=f"Expansion ratio {epsilon}"
    )


plt.xlabel("Ambient Pressure (kPa)")
plt.ylabel("Thrust (kN)")

plt.title(
    "Rocket Thrust vs Ambient Pressure"
)

plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    "NEXUS_V2_Thrust_vs_Ambient_Pressure.png",
    dpi=300
)

plt.show()


# ------------------------------------------------------------
# 13. GRAPH 3: SPECIFIC IMPULSE VS AMBIENT PRESSURE
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

for epsilon in expansion_ratios:

    subset = df[
        df["Expansion_Ratio"] == epsilon
    ].sort_values("Ambient_Pressure_Pa")

    plt.plot(
        subset["Ambient_Pressure_Pa"] / 1000,
        subset["Specific_Impulse_s"],
        marker="o",
        label=f"Expansion ratio {epsilon}"
    )


plt.xlabel("Ambient Pressure (kPa)")
plt.ylabel("Specific Impulse (s)")

plt.title(
    "Specific Impulse vs Ambient Pressure"
)

plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    "NEXUS_V2_Specific_Impulse.png",
    dpi=300
)

plt.show()


# ------------------------------------------------------------
# 14. GRAPH 4: THRUST VS EXPANSION RATIO
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

for Pa in sorted(ambient_pressures):

    subset = df[
        df["Ambient_Pressure_Pa"] == Pa
    ].sort_values("Expansion_Ratio")

    plt.plot(
        subset["Expansion_Ratio"],
        subset["Thrust_N"] / 1000,
        marker="o",
        label=f"{Pa / 1000:g} kPa"
    )


plt.xlabel("Nozzle Expansion Ratio")
plt.ylabel("Thrust (kN)")

plt.title(
    "Effect of Expansion Ratio on Thrust "
    "at Different Ambient Pressures"
)

plt.legend(title="Ambient Pressure")
plt.grid(True)
plt.tight_layout()

plt.savefig(
    "NEXUS_V2_Thrust_vs_Expansion_Ratio.png",
    dpi=300
)

plt.show()


# ------------------------------------------------------------
# 15. VALIDATION 1: CHOKED FLOW CONDITION
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("MODEL VALIDATION")
print("=" * 60)


critical_pressure_ratio = (
    2 / (gamma + 1)
)**(
    gamma / (gamma - 1)
)


maximum_ambient_ratio = max(
    ambient_pressures
) / Pc


print(
    "Critical pressure ratio:",
    critical_pressure_ratio
)

print(
    "Maximum ambient/chamber pressure ratio:",
    maximum_ambient_ratio
)


assert maximum_ambient_ratio < critical_pressure_ratio

print("Choked-flow condition: PASSED")


# ------------------------------------------------------------
# 16. VALIDATION 2: SIMULATION CASE COUNT
# ------------------------------------------------------------

expected_cases = (
    len(expansion_ratios) *
    len(ambient_pressures)
)


assert len(df) == expected_cases

print("Simulation case count: PASSED")


# ------------------------------------------------------------
# 17. VALIDATION 3: MASS FLOW CONSISTENCY
# ------------------------------------------------------------

mdot = calculate_mass_flow(
    Pc,
    Tc,
    At,
    gamma,
    R
)


assert np.allclose(
    df["Mass_Flow_kg_s"],
    mdot,
    rtol=1e-9
)

print("Mass-flow consistency: PASSED")


# ------------------------------------------------------------
# 18. VALIDATION 4: THRUST COMPONENT CONSISTENCY
# ------------------------------------------------------------

assert np.allclose(
    df["Momentum_Thrust_N"] +
    df["Pressure_Thrust_N"],
    df["Thrust_N"],
    rtol=1e-9
)

print("Thrust component consistency: PASSED")


# ------------------------------------------------------------
# 19. VALIDATION 5: SPECIFIC IMPULSE CONSISTENCY
# ------------------------------------------------------------

calculated_isp = (
    df["Thrust_N"] /
    (df["Mass_Flow_kg_s"] * g0)
)


assert np.allclose(
    calculated_isp,
    df["Specific_Impulse_s"],
    rtol=1e-9
)

print("Specific impulse consistency: PASSED")


# ------------------------------------------------------------
# 20. VALIDATION 6: EXIT MACH TREND
# ------------------------------------------------------------

mach_by_expansion = (
    df.groupby("Expansion_Ratio")["Exit_Mach"].first()
)


assert mach_by_expansion.is_monotonic_increasing

print("Exit Mach trend: PASSED")


# ------------------------------------------------------------
# 21. VALIDATION 7: EXIT PRESSURE TREND
# ------------------------------------------------------------

pressure_by_expansion = (
    df.groupby("Expansion_Ratio")["Exit_Pressure_Pa"].first()
)


assert pressure_by_expansion.is_monotonic_decreasing

print("Exit pressure trend: PASSED")


# ------------------------------------------------------------
# 22. VALIDATION 8: PRESSURE THRUST TREND
# ------------------------------------------------------------

for epsilon in expansion_ratios:

    subset = df[
        df["Expansion_Ratio"] == epsilon
    ].sort_values("Ambient_Pressure_Pa")

    assert (
        subset["Pressure_Thrust_N"].is_monotonic_decreasing
    )


print("Pressure-thrust trend: PASSED")


# ------------------------------------------------------------
# 23. VALIDATION 9: AREA-MACH SOLVER ACCURACY
# ------------------------------------------------------------

for epsilon in expansion_ratios:

    Me = calculate_exit_mach(
        epsilon,
        gamma
    )

    calculated_area_ratio = area_mach(
        Me,
        gamma
    )

    assert np.isclose(
        calculated_area_ratio,
        epsilon,
        rtol=1e-8
    )


print("Area-Mach solver accuracy: PASSED")


# ------------------------------------------------------------
# 24. FINAL VALIDATION SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 60)

print("ALL ADDITIONAL MODEL CHECKS PASSED")

print("=" * 60)


# ------------------------------------------------------------
# 25. DISPLAY SUMMARY OF PERFORMANCE
# ------------------------------------------------------------

print("\nTHRUST SUMMARY BY AMBIENT PRESSURE")

thrust_summary = df.pivot(
    index="Ambient_Pressure_Pa",
    columns="Expansion_Ratio",
    values="Thrust_N"
)

display(
    (thrust_summary / 1000).round(3)
)


print("\nSPECIFIC IMPULSE SUMMARY")

isp_summary = df.pivot(
    index="Ambient_Pressure_Pa",
    columns="Expansion_Ratio",
    values="Specific_Impulse_s"
)

display(
    isp_summary.round(3)
)


print("\nNEXUS 3.0 VERSION 2 SIMULATION COMPLETED.")

# ============================================================
# END OF PROGRAM
# ============================================================

baseline = df[
    (df["Expansion_Ratio"] == 20) &
    (df["Ambient_Pressure_Pa"] == 101325)
]

print("BASELINE NOZZLE PERFORMANCE")
print("=" * 50)

columns = [
    "Expansion_Ratio",
    "Exit_Mach",
    "Exit_Pressure_Pa",
    "Exit_Temperature_K",
    "Exit_Velocity_m_s",
    "Mass_Flow_kg_s",
    "Momentum_Thrust_N",
    "Pressure_Thrust_N",
    "Thrust_N",
    "Specific_Impulse_s",
    "Flow_Regime"
]

print(baseline[columns].to_string(index=False))

# DAY 4: EXPANSION-RATIO PARAMETRIC ANALYSIS

reference_pressure = 20000

parametric_data = df[
    df["Ambient_Pressure_Pa"] == reference_pressure
].copy()

parametric_data = parametric_data.sort_values("Expansion_Ratio")

comparison_columns = [
    "Expansion_Ratio",
    "Exit_Mach",
    "Exit_Pressure_Pa",
    "Exit_Temperature_K",
    "Exit_Velocity_m_s",
    "Momentum_Thrust_N",
    "Pressure_Thrust_N",
    "Thrust_N",
    "Specific_Impulse_s",
    "Flow_Regime"
]

print("DAY 4: EXPANSION-RATIO COMPARISON")
print("=" * 90)
print(f"Reference ambient pressure: {reference_pressure} Pa")
print(parametric_data[comparison_columns].to_string(index=False))

parametric_data.to_csv(
    "NEXUS_Day4_Parametric_Analysis.csv",
    index=False
)

import matplotlib.pyplot as plt

plt.figure(figsize=(8, 5))

plt.plot(
    parametric_data["Expansion_Ratio"],
    parametric_data["Exit_Mach"],
    marker="o"
)

plt.xlabel("Nozzle Expansion Ratio")
plt.ylabel("Exit Mach Number")
plt.title("Effect of Expansion Ratio on Exit Mach Number")
plt.grid(True)

plt.savefig("NEXUS_Day4_Exit_Mach.png", dpi=300, bbox_inches="tight")
plt.show()

plt.figure(figsize=(8, 5))

plt.plot(
    parametric_data["Expansion_Ratio"],
    parametric_data["Exit_Velocity_m_s"],
    marker="o"
)

plt.xlabel("Nozzle Expansion Ratio")
plt.ylabel("Exit Velocity (m/s)")
plt.title("Effect of Expansion Ratio on Exhaust Velocity")
plt.grid(True)

plt.savefig("NEXUS_Day4_Exit_Velocity.png", dpi=300, bbox_inches="tight")
plt.show()

plt.figure(figsize=(8, 5))

plt.plot(
    parametric_data["Expansion_Ratio"],
    parametric_data["Thrust_N"] / 1000,
    marker="o"
)

plt.xlabel("Nozzle Expansion Ratio")
plt.ylabel("Net Thrust (kN)")
plt.title("Effect of Expansion Ratio on Net Thrust at 20 kPa")
plt.grid(True)

plt.savefig("NEXUS_Day4_Thrust.png", dpi=300, bbox_inches="tight")
plt.show()

first = parametric_data.iloc[0]
last = parametric_data.iloc[-1]

parameters = [
    "Exit_Mach",
    "Exit_Pressure_Pa",
    "Exit_Velocity_m_s",
    "Thrust_N",
    "Specific_Impulse_s"
]

print("PERFORMANCE CHANGE: EXPANSION RATIO 5 TO 80")
print("=" * 60)

for parameter in parameters:

    initial = first[parameter]
    final = last[parameter]

    percentage_change = ((final - initial) / abs(initial)) * 100

    print(
        f"{parameter}: "
        f"{initial:.3f} -> {final:.3f} "
        f"({percentage_change:+.2f}%)"
    )

  # DAY 5: ATMOSPHERIC PRESSURE ANALYSIS

ambient_summary = df.pivot(
    index="Ambient_Pressure_Pa",
    columns="Expansion_Ratio",
    values="Thrust_N"
)

ambient_summary = ambient_summary.sort_index(ascending=False)

print("THRUST COMPARISON ACROSS AMBIENT PRESSURES")
print("=" * 80)

print((ambient_summary / 1000).round(3))

ambient_summary.to_csv(
    "NEXUS_Day5_Thrust_Comparison.csv"
)

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))

for ratio in sorted(df["Expansion_Ratio"].unique()):

    subset = df[df["Expansion_Ratio"] == ratio].sort_values(
        "Ambient_Pressure_Pa"
    )

    plt.plot(
        subset["Ambient_Pressure_Pa"],
        subset["Thrust_N"] / 1000,
        marker="o",
        label=f"Expansion Ratio {ratio}"
    )

plt.xscale("log")
plt.xlabel("Ambient Pressure (Pa)")
plt.ylabel("Net Thrust (kN)")
plt.title("Effect of Ambient Pressure on Rocket Nozzle Thrust")
plt.grid(True)
plt.legend()

plt.savefig(
    "NEXUS_Day5_Thrust_vs_Ambient_Pressure.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# Identify the maximum calculated thrust at each ambient pressure

best_configurations = df.loc[
    df.groupby("Ambient_Pressure_Pa")["Thrust_N"].idxmax()
].sort_values("Ambient_Pressure_Pa", ascending=False)

print("BEST TESTED EXPANSION RATIO AT EACH AMBIENT PRESSURE")
print("=" * 80)

print(
    best_configurations[
        [
            "Ambient_Pressure_Pa",
            "Expansion_Ratio",
            "Thrust_N",
            "Specific_Impulse_s",
            "Flow_Regime"
        ]
    ].to_string(index=False)
)

best_configurations.to_csv(
    "NEXUS_Day5_Best_Configurations.csv",
    index=False
)

plt.figure(figsize=(10, 6))

for ratio in sorted(df["Expansion_Ratio"].unique()):

    subset = df[df["Expansion_Ratio"] == ratio].sort_values(
        "Ambient_Pressure_Pa"
    )

    plt.plot(
        subset["Ambient_Pressure_Pa"],
        subset["Specific_Impulse_s"],
        marker="o",
        label=f"Expansion Ratio {ratio}"
    )

plt.xscale("log")
plt.xlabel("Ambient Pressure (Pa)")
plt.ylabel("Specific Impulse (s)")
plt.title("Effect of Ambient Pressure on Specific Impulse")
plt.grid(True)
plt.legend()

plt.savefig(
    "NEXUS_Day5_Specific_Impulse_vs_Ambient_Pressure.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# Compare thrust at 101325 Pa and 100 Pa

print("THRUST VARIATION ACROSS ATMOSPHERIC CONDITIONS")
print("=" * 70)

for ratio in sorted(df["Expansion_Ratio"].unique()):

    subset = df[df["Expansion_Ratio"] == ratio]

    sea_level = subset[
        subset["Ambient_Pressure_Pa"] == 101325
    ]["Thrust_N"].iloc[0]

    near_vacuum = subset[
        subset["Ambient_Pressure_Pa"] == 100
    ]["Thrust_N"].iloc[0]

    change = (
        (near_vacuum - sea_level) / abs(sea_level)
    ) * 100

    print(
        f"Expansion Ratio {ratio}: "
        f"Sea Level = {sea_level/1000:.3f} kN | "
        f"Near Vacuum = {near_vacuum/1000:.3f} kN | "
        f"Change = {change:+.2f}%"
    )

    # DAY 6: MULTI-OBJECTIVE OPTIMISATION

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Calculate performance statistics for each expansion ratio

optimisation_summary = (
    df.groupby("Expansion_Ratio")
    .agg(
        Average_Thrust_N=("Thrust_N", "mean"),
        Minimum_Thrust_N=("Thrust_N", "min"),
        Maximum_Thrust_N=("Thrust_N", "max"),
        Thrust_Std_Dev_N=("Thrust_N", "std")
    )
    .reset_index()
)

optimisation_summary["Average_Thrust_kN"] = (
    optimisation_summary["Average_Thrust_N"] / 1000
)

optimisation_summary["Minimum_Thrust_kN"] = (
    optimisation_summary["Minimum_Thrust_N"] / 1000
)

optimisation_summary["Maximum_Thrust_kN"] = (
    optimisation_summary["Maximum_Thrust_N"] / 1000
)

print("DAY 6: MULTI-CONDITION PERFORMANCE SUMMARY")
print("=" * 85)

print(
    optimisation_summary[
        [
            "Expansion_Ratio",
            "Average_Thrust_kN",
            "Minimum_Thrust_kN",
            "Maximum_Thrust_kN",
            "Thrust_Std_Dev_N"
        ]
    ].round(3).to_string(index=False)
)

optimisation_summary.to_csv(
    "NEXUS_Day6_Optimisation_Summary.csv",
    index=False
)

# Rank configurations by average thrust

ranked_configurations = optimisation_summary.sort_values(
    "Average_Thrust_N",
    ascending=False
).copy()

ranked_configurations["Performance_Rank"] = range(
    1, len(ranked_configurations) + 1
)

print("OVERALL EXPANSION RATIO RANKING")
print("=" * 60)

print(
    ranked_configurations[
        [
            "Performance_Rank",
            "Expansion_Ratio",
            "Average_Thrust_kN",
            "Minimum_Thrust_kN"
        ]
    ].round(3).to_string(index=False)
)

best_average = ranked_configurations.iloc[0]

print("\nBEST CONFIGURATION BY AVERAGE THRUST")
print(f"Expansion ratio: {best_average['Expansion_Ratio']}")
print(f"Average thrust: {best_average['Average_Thrust_kN']:.3f} kN")

plt.figure(figsize=(9, 6))

plt.scatter(
    optimisation_summary["Minimum_Thrust_kN"],
    optimisation_summary["Average_Thrust_kN"],
    s=100
)

for _, row in optimisation_summary.iterrows():

    plt.annotate(
        f"ε = {int(row['Expansion_Ratio'])}",
        (
            row["Minimum_Thrust_kN"],
            row["Average_Thrust_kN"]
        ),
        xytext=(6, 6),
        textcoords="offset points"
    )

plt.xlabel("Minimum Thrust Across Conditions (kN)")
plt.ylabel("Average Thrust Across Conditions (kN)")
plt.title("Trade-off Between Average and Worst-Case Nozzle Performance")
plt.grid(True)

plt.savefig(
    "NEXUS_Day6_Multiobjective_Tradeoff.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# Pareto analysis: maximise average thrust and minimum thrust

pareto_results = []

for _, candidate in optimisation_summary.iterrows():

    dominated = False

    for _, competitor in optimisation_summary.iterrows():

        if candidate["Expansion_Ratio"] == competitor["Expansion_Ratio"]:
            continue

        better_or_equal = (
            competitor["Average_Thrust_N"] >= candidate["Average_Thrust_N"]
            and
            competitor["Minimum_Thrust_N"] >= candidate["Minimum_Thrust_N"]
        )

        strictly_better = (
            competitor["Average_Thrust_N"] > candidate["Average_Thrust_N"]
            or
            competitor["Minimum_Thrust_N"] > candidate["Minimum_Thrust_N"]
        )

        if better_or_equal and strictly_better:
            dominated = True
            break

    pareto_results.append(not dominated)

optimisation_summary["Pareto_Optimal"] = pareto_results

print("PARETO OPTIMAL CONFIGURATIONS")
print("=" * 60)

print(
    optimisation_summary[
        [
            "Expansion_Ratio",
            "Average_Thrust_kN",
            "Minimum_Thrust_kN",
            "Pareto_Optimal"
        ]
    ].round(3).to_string(index=False)
)

optimisation_summary.to_csv(
    "NEXUS_Day6_Pareto_Analysis.csv",
    index=False
)

# DAY 7 - CODE 1: INDEPENDENT THEORETICAL VERIFICATION

import numpy as np
import pandas as pd
from scipy.optimize import brentq

# Re-state the baseline model inputs
Pc_ref = 5.0e6
Tc_ref = 3500.0
gamma_ref = 1.22
R_ref = 355.0
At_ref = 0.01
g0_ref = 9.80665

# Independent area-Mach relation
def verify_area_mach(M, gamma):
    return (
        (1 / M) *
        (
            (2 / (gamma + 1)) *
            (1 + ((gamma - 1) / 2) * M**2)
        ) ** ((gamma + 1) / (2 * (gamma - 1)))
    )

# Independent supersonic Mach solver
def verify_exit_mach(epsilon, gamma):
    return brentq(
        lambda M: verify_area_mach(M, gamma) - epsilon,
        1.000001,
        20.0
    )

# Independent choked mass-flow calculation
def verify_mass_flow(Pc, Tc, At, gamma, R):
    return (
        At * Pc *
        np.sqrt(gamma / (R * Tc)) *
        (2 / (gamma + 1)) **
        ((gamma + 1) / (2 * (gamma - 1)))
    )

# Independently calculate the 36 cases
verification_rows = []

for epsilon in sorted(df["Expansion_Ratio"].unique()):

    Me = verify_exit_mach(epsilon, gamma_ref)

    Te = Tc_ref / (
        1 + ((gamma_ref - 1) / 2) * Me**2
    )

    Pe = Pc_ref * (
        1 + ((gamma_ref - 1) / 2) * Me**2
    ) ** (-gamma_ref / (gamma_ref - 1))

    Ve = Me * np.sqrt(gamma_ref * R_ref * Te)

    mdot = verify_mass_flow(
        Pc_ref, Tc_ref, At_ref, gamma_ref, R_ref
    )

    Ae = epsilon * At_ref

    for Pa in sorted(df["Ambient_Pressure_Pa"].unique()):

        momentum_thrust = mdot * Ve
        pressure_thrust = (Pe - Pa) * Ae
        thrust = momentum_thrust + pressure_thrust
        isp = thrust / (mdot * g0_ref)

        verification_rows.append({
            "Expansion_Ratio": epsilon,
            "Ambient_Pressure_Pa": Pa,
            "Exit_Mach": Me,
            "Exit_Pressure_Pa": Pe,
            "Exit_Temperature_K": Te,
            "Exit_Velocity_m_s": Ve,
            "Mass_Flow_kg_s": mdot,
            "Momentum_Thrust_N": momentum_thrust,
            "Pressure_Thrust_N": pressure_thrust,
            "Thrust_N": thrust,
            "Specific_Impulse_s": isp
        })

verification_df = pd.DataFrame(verification_rows)

# Compare independent calculations with the original simulation
comparison = df.merge(
    verification_df,
    on=["Expansion_Ratio", "Ambient_Pressure_Pa"],
    suffixes=("_original", "_independent")
)

parameters_to_check = [
    "Exit_Mach",
    "Exit_Pressure_Pa",
    "Exit_Temperature_K",
    "Exit_Velocity_m_s",
    "Mass_Flow_kg_s",
    "Momentum_Thrust_N",
    "Pressure_Thrust_N",
    "Thrust_N",
    "Specific_Impulse_s"
]

print("INDEPENDENT THEORETICAL VERIFICATION")
print("=" * 65)

for parameter in parameters_to_check:

    original = comparison[f"{parameter}_original"]
    independent = comparison[f"{parameter}_independent"]

    max_difference = np.max(np.abs(original - independent))

    print(
        f"{parameter}: maximum absolute difference = "
        f"{max_difference:.10e}"
    )

print("\nNumber of independently recalculated cases:", len(verification_df))

# DAY 7 - CODE 2: PHYSICAL CONSISTENCY CHECKS

checks = {}

# 1. All calculated exit Mach numbers should be supersonic
checks["All exit Mach numbers are supersonic"] = (
    (verification_df["Exit_Mach"] > 1).all()
)

# 2. Exit Mach should increase with expansion ratio
mach_by_ratio = (
    verification_df.groupby("Expansion_Ratio")["Exit_Mach"].first()
)

checks["Exit Mach increases with expansion ratio"] = (
    mach_by_ratio.is_monotonic_increasing
)

# 3. Exit pressure should decrease with expansion ratio
pressure_by_ratio = (
    verification_df.groupby("Expansion_Ratio")["Exit_Pressure_Pa"].first()
)

checks["Exit pressure decreases with expansion ratio"] = (
    pressure_by_ratio.is_monotonic_decreasing
)

# 4. Mass flow should remain constant across all 36 cases
checks["Mass flow remains constant"] = np.allclose(
    verification_df["Mass_Flow_kg_s"],
    verification_df["Mass_Flow_kg_s"].iloc[0],
    rtol=1e-10
)

# 5. Thrust components should add up
checks["Thrust components sum correctly"] = np.allclose(
    verification_df["Thrust_N"],
    verification_df["Momentum_Thrust_N"] +
    verification_df["Pressure_Thrust_N"],
    rtol=1e-10
)

# 6. Specific impulse should match its defining equation
calculated_isp = (
    verification_df["Thrust_N"] /
    (verification_df["Mass_Flow_kg_s"] * g0_ref)
)

checks["Specific impulse equation is consistent"] = np.allclose(
    verification_df["Specific_Impulse_s"],
    calculated_isp,
    rtol=1e-10
)

print("PHYSICAL CONSISTENCY CHECKS")
print("=" * 65)

for name, passed in checks.items():
    print(f"{name}: {'PASS' if passed else 'FAIL'}")

print("\nTotal checks passed:", sum(checks.values()), "/", len(checks))

# DAY 7 - CODE 3: ONE-AT-A-TIME SENSITIVITY ANALYSIS

sensitivity_cases = {
    "Chamber Pressure": [4.5e6, 5.0e6, 5.5e6],
    "Chamber Temperature": [3150, 3500, 3850],
    "Specific Heat Ratio": [1.18, 1.22, 1.26]
}

ambient_pressures = sorted(
    df["Ambient_Pressure_Pa"].unique()
)

expansion_ratios = sorted(
    df["Expansion_Ratio"].unique()
)

sensitivity_rows = []

for parameter, values in sensitivity_cases.items():

    for value in values:

        # Reset all parameters to baseline
        Pc = Pc_ref
        Tc = Tc_ref
        gamma = gamma_ref

        # Change only the selected parameter
        if parameter == "Chamber Pressure":
            Pc = value

        elif parameter == "Chamber Temperature":
            Tc = value

        elif parameter == "Specific Heat Ratio":
            gamma = value

        for epsilon in expansion_ratios:

            Me = verify_exit_mach(epsilon, gamma)

            Te = Tc / (
                1 + ((gamma - 1) / 2) * Me**2
            )

            Pe = Pc * (
                1 + ((gamma - 1) / 2) * Me**2
            ) ** (-gamma / (gamma - 1))

            Ve = Me * np.sqrt(gamma * R_ref * Te)

            mdot = verify_mass_flow(
                Pc, Tc, At_ref, gamma, R_ref
            )

            Ae = epsilon * At_ref

            for Pa in ambient_pressures:

                thrust = (
                    mdot * Ve +
                    (Pe - Pa) * Ae
                )

                isp = thrust / (mdot * g0_ref)

                sensitivity_rows.append({
                    "Parameter": parameter,
                    "Parameter_Value": value,
                    "Expansion_Ratio": epsilon,
                    "Ambient_Pressure_Pa": Pa,
                    "Thrust_N": thrust,
                    "Specific_Impulse_s": isp,
                    "Mass_Flow_kg_s": mdot
                })

sensitivity_df = pd.DataFrame(sensitivity_rows)

# Average thrust across all six ambient pressures
sensitivity_summary = (
    sensitivity_df.groupby(
        ["Parameter", "Parameter_Value", "Expansion_Ratio"]
    )
    .agg(
        Average_Thrust_N=("Thrust_N", "mean"),
        Minimum_Thrust_N=("Thrust_N", "min"),
        Average_Isp_s=("Specific_Impulse_s", "mean")
    )
    .reset_index()
)

sensitivity_summary["Average_Thrust_kN"] = (
    sensitivity_summary["Average_Thrust_N"] / 1000
)

print("SENSITIVITY ANALYSIS RESULTS")
print("=" * 75)

print(
    sensitivity_summary[
        [
            "Parameter",
            "Parameter_Value",
            "Expansion_Ratio",
            "Average_Thrust_kN",
            "Minimum_Thrust_N",
            "Average_Isp_s"
        ]
    ].round(4).to_string(index=False)
)

sensitivity_summary.to_csv(
    "NEXUS_Day7_Sensitivity_Results.csv",
    index=False
)

# DAY 7 - CODE 4: SENSITIVITY GRAPHS

import matplotlib.pyplot as plt

plot_settings = [
    ("Chamber Pressure", "Chamber Pressure (Pa)",
     "Effect of Chamber Pressure on Average Thrust",
     "NEXUS_Day7_Pressure_Sensitivity.png"),

    ("Chamber Temperature", "Chamber Temperature (K)",
     "Effect of Chamber Temperature on Average Thrust",
     "NEXUS_Day7_Temperature_Sensitivity.png"),

    ("Specific Heat Ratio", "Specific Heat Ratio (gamma)",
     "Effect of Specific Heat Ratio on Average Thrust",
     "NEXUS_Day7_Gamma_Sensitivity.png")
]

for parameter, xlabel, title, filename in plot_settings:

    plt.figure(figsize=(9, 6))

    subset = sensitivity_summary[
        sensitivity_summary["Parameter"] == parameter
    ]

    for epsilon in expansion_ratios:

        curve = subset[
            subset["Expansion_Ratio"] == epsilon
        ].sort_values("Parameter_Value")

        plt.plot(
            curve["Parameter_Value"],
            curve["Average_Thrust_kN"],
            marker="o",
            label=f"Expansion Ratio {epsilon}"
        )

    plt.xlabel(xlabel)
    plt.ylabel("Average Thrust (kN)")
    plt.title(title)
    plt.grid(True)
    plt.legend()

    plt.savefig(
        filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

    # DAY 7 - CODE 5: PARAMETER SENSITIVITY COMPARISON

print("PARAMETER SENSITIVITY COMPARISON")
print("=" * 70)

for parameter, values in sensitivity_cases.items():

    lower_value = min(values)
    upper_value = max(values)

    lower = sensitivity_summary[
        (sensitivity_summary["Parameter"] == parameter) &
        (sensitivity_summary["Parameter_Value"] == lower_value)
    ]

    upper = sensitivity_summary[
        (sensitivity_summary["Parameter"] == parameter) &
        (sensitivity_summary["Parameter_Value"] == upper_value)
    ]

    merged = lower.merge(
        upper,
        on="Expansion_Ratio",
        suffixes=("_low", "_high")
    )

    percentage_change = (
        (merged["Average_Thrust_N_high"] -
         merged["Average_Thrust_N_low"]) /
        abs(merged["Average_Thrust_N_low"])
    ) * 100

    print(f"\n{parameter}")
    print(
        f"Expansion ratio 5 to 80: "
        f"{percentage_change.iloc[0]:.3f}% to "
        f"{percentage_change.iloc[-1]:.3f}%"
    )

    # DAY 8: MASTER RESEARCH RESULTS

with pd.ExcelWriter(
    "NEXUS_3.0_Master_Research_Results.xlsx"
) as writer:

    df.to_excel(
        writer,
        sheet_name="36 Simulations",
        index=False
    )

    optimisation_summary.to_excel(
        writer,
        sheet_name="Optimisation",
        index=False
    )

    sensitivity_summary.to_excel(
        writer,
        sheet_name="Sensitivity",
        index=False
    )

    verification_df.to_excel(
        writer,
        sheet_name="Independent Verification",
        index=False
    )

    # Best tested configuration at each ambient pressure
    best_configurations.to_excel(
        writer,
        sheet_name="Best Configurations",
        index=False
    )

print("Master research workbook generated successfully.")

# DAY 8: FINAL OPTIMISATION COMPARISON

final_ranking = optimisation_summary.sort_values(
    "Average_Thrust_N",
    ascending=False
).copy()

final_ranking["Rank"] = range(1, len(final_ranking) + 1)

final_ranking["Average_Thrust_kN"] = (
    final_ranking["Average_Thrust_N"] / 1000
)

final_ranking["Minimum_Thrust_kN"] = (
    final_ranking["Minimum_Thrust_N"] / 1000
)

print("FINAL NOZZLE CONFIGURATION RANKING")
print("=" * 75)

print(
    final_ranking[
        [
            "Rank",
            "Expansion_Ratio",
            "Average_Thrust_kN",
            "Minimum_Thrust_kN",
            "Thrust_Std_Dev_N"
        ]
    ].round(4).to_string(index=False)
)

print("\nSELECTED CONFIGURATION:")
print(
    "Expansion ratio:",
    final_ranking.iloc[0]["Expansion_Ratio"]
)

print(
    "Average thrust:",
    round(final_ranking.iloc[0]["Average_Thrust_kN"], 4),
    "kN"
)

# DAY 8: FINAL PERFORMANCE COMPARISON

plt.figure(figsize=(10, 6))

plt.bar(
    final_ranking["Expansion_Ratio"].astype(str),
    final_ranking["Average_Thrust_kN"]
)

plt.xlabel("Nozzle Expansion Ratio")
plt.ylabel("Average Thrust (kN)")
plt.title("Overall Nozzle Performance Across Atmospheric Conditions")
plt.grid(axis="y")

plt.savefig(
    "NEXUS_Day8_Final_Optimisation.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# Download outputs when running in Google Colab (skipped elsewhere)

try:
    from google.colab import files
except ImportError:
    files = None

if files is not None:

    # Original simulation outputs
    files.download("NEXUS_V2_Simulation_Data.csv")
    files.download("NEXUS_V2_Exit_Mach.png")
    files.download("NEXUS_V2_Thrust_vs_Ambient_Pressure.png")
    files.download("NEXUS_V2_Specific_Impulse.png")
    files.download("NEXUS_V2_Thrust_vs_Expansion_Ratio.png")

    # Day 4
    files.download("NEXUS_Day4_Parametric_Analysis.csv")
    files.download("NEXUS_Day4_Exit_Mach.png")
    files.download("NEXUS_Day4_Exit_Velocity.png")
    files.download("NEXUS_Day4_Thrust.png")

    # Day 5
    files.download("NEXUS_Day5_Thrust_Comparison.csv")
    files.download("NEXUS_Day5_Thrust_vs_Ambient_Pressure.png")
    files.download("NEXUS_Day5_Best_Configurations.csv")
    files.download("NEXUS_Day5_Specific_Impulse_vs_Ambient_Pressure.png")

    # Day 6
    files.download("NEXUS_Day6_Optimisation_Summary.csv")
    files.download("NEXUS_Day6_Multiobjective_Tradeoff.png")
    files.download("NEXUS_Day6_Pareto_Analysis.csv")

    # Day 7
    files.download("NEXUS_Day7_Sensitivity_Results.csv")
    files.download("NEXUS_Day7_Pressure_Sensitivity.png")
    files.download("NEXUS_Day7_Temperature_Sensitivity.png")
    files.download("NEXUS_Day7_Gamma_Sensitivity.png")

    # Day 8
    files.download("NEXUS_3.0_Master_Research_Results.xlsx")
    files.download("NEXUS_Day8_Final_Optimisation.png")
else:
    print("\nAll outputs saved to the current folder.")
