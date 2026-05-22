# AiM Sensor Specifications

Advisory operating ranges for the 82 AiM telemetry channels in `data/raw/N.csv`.
These are not strict experimental limits; validation is advisory only.
Empty range cells denote unknown or switch-like channels.

| sensor_name | description | data_type | unit | min_range | max_range |
| --- | --- | --- | --- | --- | --- |
| Logger Temperature | Logger internal temperature | float | C | -10 | 100 |
| External Voltage | Logger external supply voltage | float | V | 8 | 16 |
| Oil Pressure | Engine oil pressure | float | bar | 0 | 10 |
| Oil Temp | Engine oil temperature | float | C | 0 | 150 |
| Rear Brake | Rear brake line pressure | float | bar | 0 | 100 |
| InlineAcc | Longitudinal acceleration | float | g | -3 | 3 |
| LateralAcc | Lateral acceleration | float | g | -3 | 3 |
| VerticalAcc | Vertical acceleration | float | g | -4 | 4 |
| RollRate | Roll rate | float | deg/s | -300 | 300 |
| PitchRate | Pitch rate | float | deg/s | -300 | 300 |
| YawRate | Yaw rate | float | deg/s | -300 | 300 |
| PreCalcGear | Pre-calculated gear | integer |  | 0 | 6 |
| ECU RPM | Engine rotational speed | integer | rpm | 0 | 14000 |
| ECU Gear 2 | Selected gear (alt) | integer | gear | 0 | 6 |
| ECU VehSpeed | Vehicle speed | float | km/h | 0 | 120 |
| ECU Gear | Selected gear | integer | gear | 0 | 6 |
| ECU WheelSpdFL | Front left wheel speed | float | km/h | 0 | 120 |
| ECU WheelSpdFR | Front right wheel speed | float | km/h | 0 | 120 |
| ECU WheelSpdRL | Rear left wheel speed | float | km/h | 0 | 120 |
| ECU WheelSpdRR | Rear right wheel speed | float | km/h | 0 | 120 |
| ECU EngLimitAct | Engine limiter active | boolean |  |  |  |
| ECU GenericSen2 | Experimental/unknown channel | float |  |  |  |
| ECU GenericSen7 | Experimental/unknown channel | float |  |  |  |
| ECU CoolantTemp | Engine coolant temperature | float | C | 0 | 120 |
| ECU FuelTrimSTB1 | Short-term fuel trim bank 1 | float | % |  |  |
| ECU FuelTrimSTB2 | Short-term fuel trim bank 2 | float | % |  |  |
| ECU TorqCIgnCorr dup 1 | Experimental/unknown channel | float | deg |  |  |
| ECU GenericSen8 | Experimental/unknown channel | float |  |  |  |
| ECU BatteryVolt | ECU battery voltage | float | V | 8 | 16 |
| ECU GenericSen9 | Experimental/unknown channel | float |  |  |  |
| ECU GenericSen10 | Experimental/unknown channel | float |  |  |  |
| ECU ThrottlePos | Throttle position | float | % | 0 | 100 |
| ECU InjDT1 | Experimental/unknown channel | float | % |  |  |
| ECU GenericSen3 | Experimental/unknown channel | float |  |  |  |
| ECU GenericSen1 | Experimental/unknown channel | float |  |  |  |
| ECU InjDT2 | Experimental/unknown channel | float | % |  |  |
| ECU GenOut1DT | Experimental/unknown channel | float | % |  |  |
| ECU AirTemp | Intake air temperature | float | C | -10 | 80 |
| ECU FuelTrimLTB1 | Long-term fuel trim bank 1 | float | % |  |  |
| ECU GearSwitch | Gear shift switch | boolean |  |  |  |
| ECU DecelCutActi | Deceleration fuel cut active | boolean |  |  |  |
| ECU TPSAct | Actual throttle position sensor | float |  | 0 | 100 |
| ECU BrakePedSw | Brake pedal switch | boolean |  |  |  |
| ECU GenericSen4 | Experimental/unknown channel | float |  |  |  |
| ECU GenericSen5 | Experimental/unknown channel | float |  |  |  |
| ECU FuelTrimLTB2 | Long-term fuel trim bank 2 | float | % |  |  |
| ECU Lambda1 | Measured lambda | float | lambda | 0.6 | 1.3 |
| ECU WheelSlip | Wheel slip | float | km/h |  |  |
| ECU WheelDiff | Wheel speed differential | float | km/h |  |  |
| ECU ClutchSw | Clutch switch | boolean |  |  |  |
| ECU FlatShSw | Flat-shift switch | boolean |  |  |  |
| ECU AuxRPMLimSw | Auxiliary RPM limit switch | boolean |  |  |  |
| ECU BatteryLtSw | Battery light switch | boolean |  |  |  |
| ECU GenericSen6 | Experimental/unknown channel | float |  |  |  |
| ECU KnockLev1 | Experimental/unknown channel | float |  |  |  |
| ECU KnockLev2 | Experimental/unknown channel | float |  |  |  |
| ECU TargLambda | Target lambda | float |  | 0.6 | 1.3 |
| Av3E9 7 | Experimental/unknown channel | float |  |  |  |
| ECU InjectionDT3 dup 1 | Experimental/unknown channel | float | % |  |  |
| ECU InjectionDT4 dup 1 | Experimental/unknown channel | float | % |  |  |
| ECU IgnitionAng1 dup 1 | Experimental/unknown channel | float | deg |  |  |
| ECU IgnitionAng2 dup 1 | Experimental/unknown channel | float | deg |  |  |
| ECU TrigCount | Experimental/unknown channel | float |  |  |  |
| ECU CheckEngLtSw | Check-engine light switch | boolean |  |  |  |
| ECU Laun Ctr Sw | Launch control switch | boolean |  |  |  |
| ECU TrigSyncLev | Trigger sync level | float |  |  |  |
| ECU TorqDrvsRPMT | Experimental/unknown channel | float | deg/s |  |  |
| ECU TorqDrvsRPME | Experimental/unknown channel | float | deg/s |  |  |
| ECU Inj Pres D | Experimental/unknown channel | float | bar |  |  |
| ECU TorDrRPMEI | Experimental/unknown channel | float | deg |  |  |
| ECU TorDrRPMIC | Experimental/unknown channel | float | deg |  |  |
| ECU IgnitionAng1 dup 2 | Experimental/unknown channel | float | deg |  |  |
| ECU TorqCIgnCorr dup 2 | Experimental/unknown channel | float | deg |  |  |
| ECU IgnitionAng2 dup 2 | Experimental/unknown channel | float | deg |  |  |
| ECU InjectionDT3 dup 2 | Experimental/unknown channel | float | % |  |  |
| ECU InjectionDT4 dup 2 | Experimental/unknown channel | float | % |  |  |
| ECU Acc Ped Pos | Accelerator pedal position | float | % |  |  |
| ECU RaceTimer | Experimental/unknown channel | float | ms |  |  |
| ECU Cru Last T S | Experimental/unknown channel | float | km/h |  |  |
| ECU Cruise Trg S | Experimental/unknown channel | float | km/h |  |  |
| ECU Crui Spd Err | Experimental/unknown channel | float | km/h |  |  |
| ECU Cruise Ctr S | Experimental/unknown channel | float |  |  |  |
