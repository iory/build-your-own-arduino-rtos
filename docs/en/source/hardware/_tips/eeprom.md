```{admonition} Column: what is EEPROM?
:class: tip

EEPROM is a small memory that keeps its contents when the power is off. Servos have one
inside, and it holds "that servo's settings" such as its ID, bus speed and direction of
rotation. The servo reads its settings from EEPROM every time it powers up, so an ID
written once stays after the power is turned off.

Values used only while running, such as the current angle and the target angle, live
in memory that is cleared when the power goes off (RAM).
```
