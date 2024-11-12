# Aim Assist 2D

Aim Assist 2D is a simple 2D aim assist for [this game](https://humanbenchmark.com/tests/aim).

## v1
Uses a simple linear function to calculate the aim direction.

## v2
Uses a "force function" based on a Gaussian function to calculate the aim direction.

## v2.1
Same as v2, but separates "virtual space" and "real space". Removed the "force function" and just uses a mapped Gaussian function. Uses a cubic function to mitigate the error between virtual and real space.

- [x] Mitigate the error between virtual and real space. The error occurs because the mapping function changes when the target disappears. We need to find a way to mitigate the 'debt' of the virtual space.
- [ ] Tune the constants.