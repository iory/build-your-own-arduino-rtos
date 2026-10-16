```{admonition} Connect one servo at a time
:class: warning

When setting IDs, connect **exactly one servo** to the PC.
New servos all arrive with the same ID (1 for Feetech, 0 for Kondo Kagaku). With two
or more servos at the same ID connected, they all answer at once, the signals collide
and nothing can be read correctly. Writing an ID in that state changes every connected
servo to the same new ID.
```
