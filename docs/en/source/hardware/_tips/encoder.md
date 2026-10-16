```{admonition} Column: what is an encoder?
:class: tip

An encoder is a sensor that measures what angle a shaft is at right now. The servo
compares the "target angle" with the "current angle" measured by the encoder and turns
the motor so that the difference gets smaller. This is how a servo can hold still at an
angle you command.

The range of angles an encoder can measure differs from servo to servo. At angles it
cannot measure, the servo does not know where it is, so it cannot move there.
```
