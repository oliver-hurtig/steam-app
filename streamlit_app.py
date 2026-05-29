import streamlit as st
import pint

from functions import calculate_steam_energy_requirements

st.set_page_config(page_title="Steam Energy Calculator", layout="wide")
st.title("Steam Energy Requirements Calculator")

st.markdown(
    """
    <style>
    input[type=number]::-webkit-outer-spin-button,
    input[type=number]::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }
    input[type=number] {
        -moz-appearance: textfield;
    }
    .stNumberInput button[data-testid="stNumberInputStepDown"],
    .stNumberInput button[data-testid="stNumberInputStepUp"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        min-width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    .stSelectbox, .stNumberInput {
        max-width: 140px;}

    .e1rw0b1u3 {
        max-width: 1100px;}
    
    </style>
    """,
    unsafe_allow_html=True,
)

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


def value_unit_input_row(
    value_label,
    unit_choices,
    default,
    unit_index=0,
    value_help="",
    unit_help="",
    min_value=None,
    max_value=None,
    key_prefix=None,
):
    row = st.columns([1.1, 1], vertical_alignment="bottom")
    value_key = f"{key_prefix}_value" if key_prefix else f"{value_label}_value"
    unit_key = f"{key_prefix}_unit" if key_prefix else f"{value_label}_unit"

    number_input_args = {
        "value": default,
        "format": "%.1f",
        "help": value_help,
        "key": value_key,
    }
    if min_value is not None:
        number_input_args["min_value"] = min_value
    if max_value is not None:
        number_input_args["max_value"] = max_value

    value = row[0].number_input(value_label, **number_input_args)
    unit = row[1].selectbox(
        "",
        unit_choices,
        index=unit_index,
        help=unit_help,
        label_visibility="collapsed",
        key=unit_key,
    )
    return value, unit


col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.subheader("Water")
    initial_temperature, initial_temperature_unit = value_unit_input_row(
        "Temperature",
        list(TEMP_UNITS.keys()),
        15.0,
        unit_index=0,
        value_help="Initial water temperature.",
        unit_help="Initial temperature unit.",
        key_prefix="initial_temperature",
    )
    initial_pressure, initial_pressure_unit = value_unit_input_row(
        "Pressure",
        list(PRESSURE_UNITS.keys()),
        1.0,
        unit_index=0,
        value_help="Initial water pressure.",
        unit_help="Initial pressure unit.",
        key_prefix="initial_pressure",
    )

with col2:
    st.subheader("Steam")
    final_temperature, final_temperature_unit = value_unit_input_row(
        "Temperature",
        list(TEMP_UNITS.keys()),
        250.0,
        unit_index=0,
        value_help="Target steam temperature.",
        unit_help="Final temperature unit.",
        key_prefix="final_temperature",
    )
    final_pressure, final_pressure_unit = value_unit_input_row(
        "Pressure",
        list(PRESSURE_UNITS.keys()),
        25.0,
        unit_index=1,
        value_help="Target steam pressure.",
        unit_help="Final pressure unit.",
        key_prefix="final_pressure",
    )

with col3:
    st.subheader("Conversion")
    steamer_efficiency = st.number_input(
        "Steamer efficiency",
        value=0.9,
        min_value=0.01,
        max_value=1.0,
        step=0.01,
        format="%.2f",
        help="Enter as fraction (from 0.01 to 1). The steam boiler efficiency depends on the installation. It can vary from 75% for [older installation](https://ecoquery.ecoinvent.org/3.12/cutoff/dataset/4521/documentation), to [95%](https://www.sciencedirect.com/topics/engineering/boiler-efficiency). The use of [heat pump for steam generation](https://www.sciencedirect.com/science/article/pii/S0196890423012281) could significantly reduce the amount of energy consumed.",
    )
    LHV_natural_gas, LHV_unit = value_unit_input_row(
        "Natural gas LHV",
        list(LHV_UNITS.keys()),
        39.5,
        unit_index=0,
        value_help="""Lower heating value of natural gas.
        Generally in a range of 30-40 MJ/m³.
        The Renewable Energy Directive uses 50 MJ/kg and a density of 0.79 kg/m³ (=39.5 MJ/m³). [https://eur-lex.europa.eu/eli/dir/2018/2001/oj/eng]""",
        key_prefix="LHV_natural_gas",
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


def format_compact(quantity, digits=1):
    #compact_quantity = quantity.to_compact()
    return f"{quantity:.{digits}f~P}"

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
            format_compact(results["delta_h"], digits=1)
        )
        st.metric(
            "Energy needs",
            format_compact(results["energy_needs"], digits=1)
        )
        st.metric(
            "Natural gas volume",
            format_compact(results["NG_volume"], digits=1)
        )
        st.write(
            "Calculated energy requirements are based on steam generation from the provided initial "
            "water state to the target steam state, with the selected efficiency and fuel LHV."
        )
