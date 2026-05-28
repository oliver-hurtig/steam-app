import streamlit as st
import pint

from functions import calculate_steam_energy_requirements

st.set_page_config(page_title="Steam Energy Calculator", layout="wide")
st.title("Steam Energy Requirements Calculator")

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity

TEMP_UNITS = {
    "°C": "degC",
    "°F": "degF",
    "K": "kelvin",
}
PRESSURE_UNITS = {
    "bar": "bar",
    "psi": "psi",
    "kPa": "kilopascal",
    "Pa": "pascal",
}
LHV_UNITS = {
    "MJ/m³": "megajoule / meter ** 3",
    "kJ/m³": "kilojoule / meter ** 3",
    "BTU/ft³": "BTU / foot ** 3",
}

st.markdown(
    "Use the inputs below to calculate steam production energy requirements from water. "
    "The results update automatically when any input changes."
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Initial conditions")
    initial_temperature = st.number_input(
        "Initial temperature",
        value=15.0,
        format="%.1f",
        help="Initial water temperature.",
    )
    initial_temperature_unit = st.selectbox(
        "Initial temperature unit",
        list(TEMP_UNITS.keys()),
        index=0,
    )
    initial_pressure = st.number_input(
        "Initial pressure",
        value=1.0,
        format="%.1f",
        help="Initial water pressure.",
    )
    initial_pressure_unit = st.selectbox(
        "Initial pressure unit",
        list(PRESSURE_UNITS.keys()),
        index=0,
    )

with col2:
    st.subheader("Target steam conditions")
    final_temperature = st.number_input(
        "Final temperature",
        value=250.0,
        format="%.1f",
        help="Target steam temperature.",
    )
    final_temperature_unit = st.selectbox(
        "Final temperature unit",
        list(TEMP_UNITS.keys()),
        index=0,
    )
    final_pressure = st.number_input(
        "Final pressure",
        value=25.0,
        format="%.1f",
        help="Target steam pressure.",
    )
    final_pressure_unit = st.selectbox(
        "Final pressure unit",
        list(PRESSURE_UNITS.keys()),
        index=1,
    )

st.subheader("Steam generator inputs")
steamer_efficiency = st.number_input(
    "Steamer efficiency",
    value=0.9,
    min_value=0.01,
    max_value=1.0,
    step=0.01,
    format="%.2f",
    help="Boiler/steamer efficiency as a fraction (0-1).",
)
LHV_natural_gas = st.number_input(
    "Natural gas LHV",
    value=35.0,
    format="%.2f",
    help="Lower heating value of natural gas.",
)
LHV_unit = st.selectbox(
    "Natural gas LHV unit",
    list(LHV_UNITS.keys()),
    index=0,
)

input_error = None
results = None

try:
    T_init = Q_(initial_temperature, ureg(TEMP_UNITS[initial_temperature_unit]))
    P_init = Q_(initial_pressure, ureg(PRESSURE_UNITS[initial_pressure_unit]))
    T_target = Q_(final_temperature, ureg(TEMP_UNITS[final_temperature_unit]))
    P_target = Q_(final_pressure, ureg(PRESSURE_UNITS[final_pressure_unit]))
    LHV_value = Q_(LHV_natural_gas, ureg(LHV_UNITS[LHV_unit]))

    results = calculate_steam_energy_requirements(
        T_init=T_init,
        P_init=P_init,
        T_target=T_target,
        P_target=P_target,
        steamer_efficiency=steamer_efficiency,
        LHV_natural_gas=LHV_value,
        ureg=ureg,
    )
except Exception as exc:
    input_error = exc

st.markdown("---")
result_area = st.container()
with result_area:
    st.subheader("Calculation results")

    if input_error is not None:
        st.warning(f"Error: {input_error}")
    elif results is None:
        st.info("Enter input values and click Recalculate to see results.")
    else:
        st.metric(
            "Enthalpy change",
            f"{results['delta_h'].magnitude:.1f} {results['delta_h'].units}"
        )
        st.metric(
            "Energy needs",
            f"{results['energy_needs'].magnitude:.1f} {results['energy_needs'].units}"
        )
        st.metric(
            "Natural gas volume",
            f"{results['NG_volume'].magnitude:.1f} {results['NG_volume'].units}"
        )
        st.write(
            "Calculated energy requirements are based on steam generation from the provided initial "
            "water state to the target steam state, with the selected efficiency and fuel LHV."
        )
