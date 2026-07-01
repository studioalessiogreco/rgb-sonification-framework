# RGB Sonification Framework – Max/MSP Cross-Modal Prototype

This project presents the functional software prototype developed in Max/MSP implementing the *RGB Sonification Framework for Accessible Visual Experience* (Zenodo, 2026)[cite: 1]. The system operates as a deterministic computational tool designed to map structural resonances between chromatic inputs and invariant acoustic outputs[cite: 1].

## 1. Theoretical Framework & Artistic Paradigm

Grounded in the **Co-Perception Model**, this framework rejects the notion of sound as a static object, treating it instead as a mutable substance and an autonomous, spatial, and generative agent[cite: 1]. By deploying cross-modal latent representation systems, the prototype establishes an artificial synaesthesia where visual data is navigated through a "situated listening" paradigm[cite: 1]. 

The system operates across three core axioms of Co-Perception[cite: 1]:
* **Shared Perceptual Field:** The observer and the generative system inhabit the same spatio-temporal environment under identical acoustic conditions, dissolving the subject/object division[cite: 1].
* **Bidirectional Modulation:** An interactive coupling process where the system's output continually configures the observer's navigation, turning the composition into a chronology of modulations[cite: 1].
* **Distributed Agency:** Decision-making emerges from the collective interaction of the human-machine-environment system, making authorship a structural property rather than a predetermined individual will[cite: 1].

---

## 2. Spectral Architecture

The mapping matrix scales chromatic values into distinct spectral registers, preventing overlap to preserve acoustic legibility and leveraging logarithmic scaling based on human auditory perception[cite: 1]:

| Channel | Spectral Register | Frequency Range | Synthesis Strategy |
| :--- | :--- | :--- | :--- |
| **R (Red)** | High Frequencies | 2 kHz - 16 kHz | Bright timbres, rapid attacks, high spectral centroid.[cite: 1] |
| **G (Green)** | Mid Frequencies | 500 Hz - 2 kHz | Warm timbres, balanced harmonic content, moderate sustain.[cite: 1] |
| **B (Blue)** | Low Frequencies | 20 Hz - 500 Hz | Dense sub-bass foundations, slow attacks, rich resonance.[cite: 1] |

### Core Design Principles
* **Determinism:** Identical chromatic inputs guarantee invariant acoustic outputs[cite: 1].
* **Spectral Separation:** Complete elimination of inter-channel overlap to ensure absolute acoustic legibility[cite: 1].
* **Logarithmic Scaling:** Frequency distribution calibrated strictly to human perceptual curves[cite: 1].
* **Modularity:** Absolute functional independence between sound banks, mapping functions, and mixing stages[cite: 1].

---

## 3. Processing Pipeline

The internal Max/MSP signal flow is organized into five autonomous, modular pipeline stages[cite: 1]:

1. **Chromatic Input:** Extraction of RGB data stream via spatial averaging or Region of Interest (ROI) selection[cite: 1].
2. **Channel Decomposition:** Isolation of individual R, G, and B data parameters within a 0–255 integer domain[cite: 1].
3. **Parametric Mapping:** Transposition of numeric variables through logarithmic functions for precise amplitude and frequency scaling[cite: 1].
4. **Sound Bank Lookup:** Dynamic selection of audio assets and real-time interpolation of synthesis values[cite: 1].
5. **Mixing & Output:** Multichannel signal balancing optimized for stereo or spatial multichannel audio deployment[cite: 1].

---

## 4. Open Science & Institutional Record

This project is published under an open framework to foster accessibility research and co-agency in artistic systems[cite: 1].

* **Author:** Alessio Greco (Sound Artist & Artistic Researcher)[cite: 1]
* **Main Publication:** *RGB Sonification Framework for Accessible Visual Experience*, Zenodo (2026)[cite: 1].
* **DOI:** 10.5281/zenodo.20474031[cite: 1]
* **ORCID:** 0009-0001-3722-3772[cite: 1]
* **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)[cite: 1]
* **Contact:** studio.alessiogrc@gmail.com[cite: 1]

