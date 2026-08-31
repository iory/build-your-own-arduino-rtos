# FAQ / Troubleshooting

## About the book

### Why is it called a "real-time OS" when there is no priority scheduling?

The scheduler built in Chapter 4 is a **round-robin** scheduler driven by
SysTick with a 10 ms time slice; it does not look at task priorities.
Priority-based scheduling is Exercise 4-4 at the end of that chapter.

The book therefore does not cover what hard real-time guarantees require:
priority-based deadline analysis, schedulability analysis, or static
worst-case execution time (WCET) analysis. If that is your goal, consult
a dedicated text or the documentation of a production RTOS such as
FreeRTOS, Zephyr, or TOPPERS.

What the book does cover is the step before that:

- **How a deadline actually arises on real hardware.** In Chapter 13 the
  control loop reads back from, and writes to, eight serial bus servos
  every cycle, which creates a physical 20 ms deadline. Fire-and-forget
  PWM creates no deadline to miss in the first place.
- **What the OS needs in order to meet it.** Preemptive switching
  (Chapter 4), isolating a runaway task (Chapter 6), locks and priority
  inversion (Advanced Chapter 1, section 1.7), and estimating execution
  time from measurements with an explicit margin (Chapter 13 supplement).

Priority inversion and priority inheritance themselves are covered in
Advanced Chapter 1, section 1.7. Once you have implemented Exercise 4-4,
the exercise in 1.7 lets you reproduce priority inversion on a
priority-aware scheduler and then resolve it with priority inheritance.

## Troubleshooting

- **Board not detected**: use a data-capable USB-C cable; on Linux add
  yourself to `dialout` and re-login.
- **Upload fails midway**: double-tap the reset button to enter the
  bootloader, then retry.
- **Nothing on the serial monitor**: check the baud rate is `115200`.

Report issues with reproduction steps on
[GitHub Issues](https://github.com/iory/build-your-own-arduino-rtos/issues).
