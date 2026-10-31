# ABOUT

This module brings together the guidance for two dedicated sessions:

- "An Overall Enterprise AI Architecture Reference"
- "A Technical Coding Exercise for an Enterprise RAG Solution"

The first session presents a broad enterprise AI reference architecture. The second session narrows the discussion to the smaller Enterprise RAG coding exercise in the root repository. The reference architecture describes a target enterprise landscape; it must not be interpreted as a list of features implemented by the coding exercise.

# ABOUT "Overall Enterprise AI Architecture Reference"

The rendered presentation is `enterprise_genai_reference_architecture_presentation.pdf`. Its Markdown source is `presentation.md`.

## PRESENTATION AGENDA

1. Prerequisites and base foundations
2. High-level architecture and component relationships
3. MLOps/GenAI Ops and model serving
4. AI Gateway
5. Identity, authentication, and RBAC/ABAC authorization
6. Total AI Security
7. External GenAI model downloading
8. Cost Management and FinOps
9. Enterprise RAG and secure document search
10. Agentic AI applications and MCP
11. Evaluation, benchmarking, A/B testing, and canary deployment
12. Internal copilots and future multimodal capabilities
13. Platform operating model and team responsibilities
14. Technical and organizational development roadmaps
15. AI ethics and the EU AI Act

## FOLLOWING THE FILE

- The presentation aims to explain an enterprise end-to-end AI baseline/reference architecture.
- The PDF is divided into logically separated pages and sections. Use `presentation.md` as the readable source of the narrative and embedded Mermaid diagrams.
- The standalone `.mmd` files in this directory contain the main Mermaid architecture diagrams. The corresponding rendered PNG files are under `./image`.
- If you have difficulty reading the diagrams due to resolution issues, the following files will help:
  - `presentation.md`: It is the raw source of the presentation. You can read it in any Markdown editor.
  - If you have trouble focusing on the Mermaid charts in the presentation PDF or `presentation.md` file, please follow the instructions below:
    - This directory contains the source Mermaid charts (`.mmd`) and the `./image` directory contains their PNG conversions, which may provide a better view than the PDF.
    - You can open a source Mermaid chart file (`.mmd`) in a regular text editor, then copy and paste it into [https://mermaid.live/](https://mermaid.live/) or [https://mermaid2img.com/editor](https://mermaid2img.com/editor) to get a better view.
    - Or you can go directly to the PNG files in the `./image` directory using a regular image viewer.

# ABOUT "A Technical Coding Exercise for an Enterprise RAG Solution"

This session explains the Enterprise RAG prototype developed in the root repository. It should demonstrate an understandable end-to-end RAG design with enterprise-oriented engineering practices, without presenting the prototype as a complete enterprise platform.

The authoritative sources are the root `AGENTS.md`, the root `README.md`, and the component READMEs. 

## PRESENTATION BOUNDARY

The coding exercise illustrates how a small RAG system can adopt enterprise-friendly boundaries, configuration, lifecycle management, source traceability, testing, documentation, and deployment planning. It does not claim to implement the broader presentation's enterprise identity, authorization, AI Gateway, total AI security, agent platform, governance, or full production high-availability architecture.
