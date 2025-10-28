"""
EnMS - Boiler Machine Simulator
Multi-Energy: Electricity + Natural Gas + Steam

Author: EnMS Team
Date: October 27, 2024
"""

from datetime import datetime
from .base_machine import BaseMachineSimulator
from models import MachineType, OperatingMode
import random
import numpy as np


class BoilerSimulator(BaseMachineSimulator):
    """
    Industrial boiler simulator with 3 energy streams:
    - INPUT: Electricity (pumps, fans, control systems) ~15% of thermal power
    - INPUT: Natural Gas (fuel for combustion) ~100% thermal capacity
    - OUTPUT: Steam (process steam) ~85% efficiency
    
    Simulates realistic industrial boiler behavior:
    - Thermal capacity ~50x electrical power (e.g., 45 kW electrical → 2250 kW thermal)
    - Natural gas: 1 m³ = 10.55 kWh thermal energy
    - Steam: 2.26 kWh/kg (latent heat at 10 bar)
    - Typical efficiency: 85%
    """
    
    def __init__(self, machine_id: str, machine_name: str, rated_power_kw: float, mqtt_topic: str):
        """
        Initialize boiler simulator.
        
        Args:
            machine_id: Unique machine identifier
            machine_name: Display name (e.g., "Boiler-1")
            rated_power_kw: Electrical power rating (pumps, fans, controls)
            mqtt_topic: Base MQTT topic for publishing
        """
        super().__init__(
            machine_id=machine_id,
            machine_name=machine_name,
            machine_type=MachineType.BOILER,
            rated_power_kw=rated_power_kw,
            data_interval_seconds=30,  # 30-second readings
            mqtt_topic=mqtt_topic
        )
        
        # Boiler-specific parameters
        self.thermal_capacity_kw = rated_power_kw * 50  # 50x electrical is typical
        self.boiler_efficiency = 0.85  # 85% efficiency
        self.steam_pressure_bar = 10.0  # 10 bar steam pressure
        self.outdoor_temp_base_c = 15.0  # Baseline outdoor temperature
        
        # Energy conversion factors
        self.gas_energy_kwh_per_m3 = 10.55  # 1 m³ natural gas = 10.55 kWh
        self.steam_energy_kwh_per_kg = 2.26  # 1 kg steam = 2.26 kWh (at 10 bar)
        
    def _generate_sensor_data(self) -> dict:
        """
        Generate multi-energy sensor readings.
        
        Returns:
            Dict with electricity, natural gas, and steam measurements
        """
        # Get base load factor (0.0 to 1.0) based on time of day
        hour = datetime.now().hour
        if 6 <= hour < 22:  # Daytime: higher load
            base_load = 0.70 + np.random.uniform(-0.15, 0.15)
        else:  # Nighttime: lower load
            base_load = 0.40 + np.random.uniform(-0.10, 0.10)
        
        base_load = np.clip(base_load, 0.05, 1.0)
        
        # Operating mode affects all energy streams
        mode_multiplier = self._get_mode_multiplier()
        effective_load = base_load * mode_multiplier
        
        # Electricity: Auxiliary systems (pumps, fans, controls)
        # Scales with thermal load but not linearly (pump efficiency curves)
        electricity_kw = self.rated_power_kw * effective_load * random.uniform(0.85, 1.15)
        electricity_kwh = electricity_kw * (self.data_interval_seconds / 3600)
        
        # 2. NATURAL GAS: Fuel consumption
        # Thermal power needed = thermal_capacity × effective_load
        thermal_power_kw = self.thermal_capacity_kw * effective_load
        # Account for efficiency: need more gas input than thermal output
        gas_input_kw = thermal_power_kw / self.boiler_efficiency
        gas_flow_m3h = gas_input_kw / self.gas_energy_kwh_per_m3
        gas_consumption_m3 = gas_flow_m3h * (self.data_interval_seconds / 3600)
        
        # 3. STEAM: Output product
        # Steam produced = thermal power × efficiency
        steam_output_kw = thermal_power_kw * self.boiler_efficiency
        steam_production_kgh = steam_output_kw / self.steam_energy_kwh_per_kg
        steam_production_kg = steam_production_kgh * (self.data_interval_seconds / 3600)
        
        # Additional process variables
        boiler_efficiency_actual = self.boiler_efficiency + random.uniform(-0.03, 0.03)
        steam_pressure = self.steam_pressure_bar + random.uniform(-0.5, 0.5)
        flue_gas_temp = 180 + random.uniform(-15, 15)  # Stack temperature
        outdoor_temp = self.outdoor_temp_base_c + random.uniform(-5, 5)
        
        return {
            # Electricity readings (for energy_readings table)
            "power_kw": round(electricity_kw, 3),
            "energy_kwh": round(electricity_kwh, 4),
            "voltage_v": round(400 + random.uniform(-10, 10), 1),
            "current_a": round((electricity_kw * 1000) / (400 * 1.732 * 0.95), 2),
            
            # Natural gas readings
            "flow_rate_m3h": round(gas_flow_m3h, 3),
            "consumption_m3": round(gas_consumption_m3, 4),
            "pressure_bar": round(4.0 + random.uniform(-0.2, 0.2), 2),
            "calorific_value_kwh_m3": round(self.gas_energy_kwh_per_m3, 2),
            "temperature_c": round(20 + random.uniform(-2, 2), 1),
            
            # Steam readings
            "flow_rate_kg_h": round(steam_production_kgh, 2),
            "consumption_kg": round(steam_production_kg, 3),
            "steam_pressure_bar": round(steam_pressure, 2),
            "steam_temperature_c": round(184.0 + random.uniform(-3, 3), 1),  # ~184°C at 10 bar
            "enthalpy_kj_kg": round(2777 + random.uniform(-50, 50), 0),  # kJ/kg at 10 bar
            
            # Process variables
            "boiler_efficiency": round(boiler_efficiency_actual, 3),
            "flue_gas_temp_c": round(flue_gas_temp, 1),
            "outdoor_temp_c": round(outdoor_temp, 1),
            "operating_mode": self.operating_mode.value
        }
    
    def _get_mode_multiplier(self) -> float:
        """
        Get load multiplier based on operating mode.
        
        Returns:
            Multiplier for energy consumption (0.0 to 1.0)
        """
        if self.operating_mode == OperatingMode.IDLE:
            return 0.15  # Keep-warm mode: 15% load
        elif self.operating_mode == OperatingMode.MAINTENANCE:
            return 0.05  # Shutdown: 5% load (safety systems only)
        elif self.operating_mode == OperatingMode.FAULT:
            return 0.20  # Emergency shutdown: 20% load
        elif self.operating_mode == OperatingMode.OFFLINE:
            return 0.0  # Completely off
        else:  # RUNNING
            return 1.0  # Normal operation
    
    # ========================================================================
    # Abstract Method Implementations (required by BaseMachineSimulator)
    # ========================================================================
    
    def generate_energy_reading(self, timestamp: datetime) -> dict:
        """
        Generate electricity energy reading (primary energy input).
        This implements the abstract method from BaseMachineSimulator.
        
        Returns:
            Energy reading dict with power_kw, energy_kwh, voltage, current
        """
        sensor_data = self._generate_sensor_data()
        return {
            "timestamp": timestamp.isoformat(),
            "machine_id": self.machine_id,
            "power_kw": sensor_data["power_kw"],
            "energy_kwh": sensor_data["energy_kwh"],
            "voltage_v": sensor_data.get("voltage_v"),
            "current_a": sensor_data.get("current_a"),
            "power_factor": 0.95
        }
    
    def generate_production_data(self, timestamp: datetime) -> dict:
        """
        Generate production data (steam output as product).
        This implements the abstract method from BaseMachineSimulator.
        
        Returns:
            Production data dict with output counts/rates
        """
        sensor_data = self._generate_sensor_data()
        return {
            "timestamp": timestamp.isoformat(),
            "machine_id": self.machine_id,
            "production_count": int(sensor_data["consumption_kg"]),  # kg of steam produced
            "production_rate": sensor_data["flow_rate_kg_h"],  # kg/h
            "quality_rating": 0.98,  # Steam quality
            "defect_count": 0,
            "efficiency": sensor_data["boiler_efficiency"]
        }
    
    def generate_environmental_data(self, timestamp: datetime) -> dict:
        """
        Generate environmental data (flue gas, outdoor conditions).
        This implements the abstract method from BaseMachineSimulator.
        
        Returns:
            Environmental data dict with temperatures, humidity
        """
        sensor_data = self._generate_sensor_data()
        return {
            "timestamp": timestamp.isoformat(),
            "machine_id": self.machine_id,
            "temperature_c": sensor_data.get("outdoor_temp_c", 15.0),
            "humidity_percent": 60.0 + random.uniform(-10, 10),
            "co2_ppm": 400 + random.uniform(-50, 50),
            "pressure_mbar": 1013 + random.uniform(-5, 5)
        }
