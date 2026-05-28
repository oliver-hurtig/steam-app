import CoolProp.CoolProp as CP
import pint

# Mapping phase name and index
phase_names = {
    0: "unknown",
    1: "liquid",
    2: "supercritical",
    3: "supercritical_gas",
    4: "supercritical_liquid",
    5: "gas",
    6: "wet",
    7: "twophase",
}

def validate_steam_phase(T:pint.Quantity, P:pint.Quantity):
    """
    Validate that water is in the gaseous (steam) phase at given conditions.
    
    Parameters
    ----------
    T : pint.Quantity
        Temperature of the water/steam.
    P : pint.Quantity
        Pressure of the water/steam.
    
    Raises
    ------
    ValueError
        If the water is not in the gas or supercritical gas phase.
    """
    phase_index = CP.PropsSI(
        "Phase",
        "P",
        P.to("Pa").magnitude,
        "T",
        T.to("kelvin").magnitude,
        "water",
    )
    if phase_names[phase_index] not in ["gas", "supercritical_gas"]:
        raise ValueError(
            f"Water is not in gaseous phase. Current phase: {phase_names[phase_index]}"
        )


def calculate_steam_energy_requirements(
    T_init: pint.Quantity,
    P_init: pint.Quantity,
    T_target: pint.Quantity,
    P_target: pint.Quantity,
    steamer_efficiency: float,
    LHV_natural_gas: pint.Quantity,
    ureg,
):
    """
    Calculate the energy requirements for steam production from water.
    
    This function computes the enthalpy change required to heat water from initial
    conditions to superheated steam at target conditions, accounting for conversion
    losses and determining natural gas consumption.
    
    Parameters
    ----------
    T_init : pint.Quantity
        Initial temperature of the water (e.g., 293.15 * ureg.kelvin).
    P_init : pint.Quantity
        Initial pressure of the water (e.g., 1 * ureg.bar).
    T_target : pint.Quantity
        Target temperature of the steam (e.g., 473.15 * ureg.kelvin).
    P_target : pint.Quantity
        Target pressure of the steam (e.g., 10 * ureg.bar).
    steamer_efficiency : float
        Efficiency of the steam generation system (dimensionless, 0 < efficiency <= 1).
    LHV_natural_gas : pint.Quantity
        Lower Heating Value of natural gas (typically 30-40 MJ/m³ depending on composition).
    ureg : pint.UnitRegistry
        Pint unit registry for handling physical quantities.
    
    Returns
    -------
    dict
        Dictionary containing:
        - 'delta_h' : Enthalpy change in MJ/kg
        - 'energy_needs' : Energy required including conversion losses in MJ/kg
        - 'NG_volume' : Natural gas volume per tonne of steam in m³/ton
    
    Raises
    ------
    ValueError
        If the target conditions do not correspond to steam (gaseous phase).
    
    Notes
    -----
    The function uses CoolProp's PropsSI to calculate thermodynamic properties
    of water and steam. The natural gas lower heating value typically ranges
    from 30-40 MJ/m³ depending on gas composition.
    """
    Q_ = ureg.Quantity

    # Calculate initial enthalpy at starting conditions
    h_init = CP.PropsSI(
        "H", "P", P_init.to("Pa").magnitude, "T", T_init.to("kelvin").magnitude, "Water"
    )

    # Calculate target enthalpy at steam conditions
    h_target = CP.PropsSI(
        "H",
        "P",
        P_target.to("Pa").magnitude,
        "T",
        T_target.to("kelvin").magnitude,
        "Water",
    )

    # Validate that target conditions produce steam
    validate_steam_phase(T=T_target, P=P_target)

    # Calculate enthalpy difference (energy needed for phase change and heating)
    delta_h = Q_(h_target - h_init, ureg.J / ureg.kilogram)
    #print("Final energy needed for steam production:")
    #print(delta_h.to("MJ/kg"))

    # Account for conversion losses (e.g., boiler efficiency)
    energy_needs = delta_h / steamer_efficiency
    #print("Energy needed for steam production with conversion losses:")
    #print(energy_needs.to("MJ/kg"))

    # Calculate natural gas volume required
    NG_volume = energy_needs / LHV_natural_gas
    #print("Natural gas needs per tonne of steam:")
    #print(NG_volume.to("m**3/ton"))

    return {
        'delta_h': delta_h.to("MJ/kg"),
        'energy_needs': energy_needs.to("MJ/kg"),
        'NG_volume': NG_volume.to("m**3/ton")
    }
