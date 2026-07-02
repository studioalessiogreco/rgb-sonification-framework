# RGB Sonification Framework – Max/MSP Cross-Modal Prototype

This project presents the functional software prototype developed in Max/MSP implementing the *RGB Sonification Framework for Accessible Visual Experience* (Zenodo, 2026). The system operates as a deterministic computational tool designed to map structural resonances between chromatic inputs and invariant acoustic outputs.

## 1. Theoretical Framework & Artistic Paradigm

Grounded in the **Co-Perception Model**, this framework rejects the notion of sound as a static object, treating it instead as a mutable substance and an autonomous, spatial, and generative agent. By deploying cross-modal latent representation systems, the prototype establishes an artificial synaesthesia where visual data is navigated through a "situated listening" paradigm. 

The system operates across three core axioms of Co-Perception:
* **Shared Perceptual Field:** The observer and the generative system inhabit the same spatio-temporal environment under identical acoustic conditions, dissolving the subject/object division.
* **Bidirectional Modulation:** An interactive coupling process where the system's output continually configures the observer's navigation, turning the composition into a chronology of modulations.
* **Distributed Agency:** Decision-making emerges from the collective interaction of the human-machine-environment system, making authorship a structural property rather than a predetermined individual will.

---

## 2. Spectral Architecture

The mapping matrix scales chromatic values into distinct spectral registers, preventing overlap to preserve acoustic legibility and leveraging logarithmic scaling based on human auditory perception:

| Channel | Spectral Register | Frequency Range | Synthesis Strategy |
| :--- | :--- | :--- | :--- |
| **R (Red)** | High Frequencies | 2 kHz - 16 kHz | Bright timbres, rapid attacks, high spectral centroid. |
| **G (Green)** | Mid Frequencies | 500 Hz - 2 kHz | Warm timbres, balanced harmonic content, moderate sustain. |
| **B (Blue)** | Low Frequencies | 20 Hz - 500 Hz | Dense sub-bass foundations, slow attacks, rich resonance. |

### Core Design Principles
* **Determinism:** Identical chromatic inputs guarantee invariant acoustic outputs.
* **Spectral Separation:** Complete elimination of inter-channel overlap to ensure absolute acoustic legibility.
* **Logarithmic Scaling:** Frequency distribution calibrated strictly to human perceptual curves.
* **Modularity:** Absolute functional independence between sound banks, mapping functions, and mixing stages.

---

## 3. Processing Pipeline

The internal Max/MSP signal flow is organized into five autonomous, modular pipeline stages:

1. **Chromatic Input:** Extraction of RGB data stream via spatial averaging or Region of Interest (ROI) selection.
2. **Channel Decomposition:** Isolation of individual R, G, and B data parameters within a 0–255 integer domain.
3. **Parametric Mapping:** Transposition of numeric variables through logarithmic functions for precise amplitude and frequency scaling.
4. **Sound Bank Lookup:** Dynamic selection of audio assets and real-time interpolation of synthesis values.
5. **Mixing & Output:** Multichannel signal balancing optimized for stereo or spatial multichannel audio deployment.

---

## 4. Open Science & Institutional Record

This project is published under an open framework to foster accessibility research and co-agency in artistic systems.

* **Author:** Alessio Greco (Sound Artist & Artistic Researcher)
* **Main Publication:** *RGB Sonification Framework for Accessible Visual Experience*, Zenodo (2026).
* **DOI:** 10.5281/zenodo.20474031
* **ORCID:** 0009-0001-3722-3772
* **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
* **Contact:** studio.alessiogrc@gmail.com

