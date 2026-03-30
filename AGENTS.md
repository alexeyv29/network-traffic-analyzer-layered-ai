# Project Architecture & AI Guidelines: Network Traffic Analyzer

You are an autonomous AI agent operating within a strict 3-layer architecture. We are building a local web application that parses Wireshark `.pcap`/`.pcapng` files, extracts network flows and metadata, and uses an LLM to generate human-readable insights and Mermaid.js network diagrams.

## Layer 1: Directives (The "What")
- **Directory:** `/directives/`
- **Role:** This is your inbox. Read the markdown files here to understand your current objectives and tasks.
- **Rule:** Follow the instructions in the directives precisely. 

## Layer 2: Orchestration (The "How")
- **Role:** You are the orchestrator.
- **Action:** Analyze the current directive, break it down into logical steps, and decide which scripts, tools, or APIs are needed to accomplish the goal.
- **Rule:** Always check your environment for existing tools before writing new ones from scratch.

## Layer 3: Execution (The "Action")
- **Directory:** `/execution/`
- **Role:** This is your workshop. 
- **Action:** Write, execute, and debug your scripts (e.g., Python, HTML/JS) in this directory to fulfill the directive.

## Core Behaviors & Workflows
- **Self-Annealing (Error Handling):** If a script fails or you encounter an error, do not stop. You must self-correct: Fix the error -> Update the script/tool -> Update the directive document if the requirements or realities of the task have changed.
- **Artifact Management:** - Save final deliverables (like the web UI or production APIs) to the root directory or specific app folders as directed.
  - **Temporary Files:** Use the `/.tmp/` directory for any intermediate processing, scratchpad work, or test `.pcap` files. Keep the workspace clean.
- **Orchestration Log:** Always output a brief 'Orchestration Log' in the chat explaining your plan before executing Layer 3 scripts.

## Directive Execution Protocol
When you receive a directive, you must follow these steps:
1. **Acknowledge:** Confirm receipt of the directive.
2. **Plan:** Create a step-by-step plan to fulfill the directive.
3. **Execute:** Implement the plan using the tools and scripts available in the execution layer.
4. **Verify:** Test your implementation to ensure it meets the directive's requirements.
5. **Self-Anneal:** If verification fails, fix the issue and repeat the execution and verification steps.
6. **Report:** Once the directive is fulfilled, provide a summary of your work and any relevant outputs.

## Self-Annealing Protocol
When you encounter an error or unexpected behavior, you must follow these steps:
1. **Analyze:** Understand the error message and its root cause.
2. **Fix:** Modify the relevant script or configuration to address the error.
3. **Update:** Update the directive document to reflect the changes made or new requirements discovered.
4. **Retry:** Re-run the failed step and verify that the error is resolved.
5. **Document:** Record the error and its resolution in the self-annealing log.

## Artifact Management Protocol
When managing files and artifacts, you must follow these steps:
1. **Identify:** Determine which files need to be created, modified, or deleted.
2. **Organize:** Place files in the appropriate directories (e.g., `/execution/` for scripts, `/directives/` for documentation, `/.tmp/` for temporary files).
3. **Version:** Use clear and descriptive filenames to track changes.
4. **Clean:** Remove temporary files once they are no longer needed.
5. **Backup:** Before making significant changes, create backups of important files.

## Self-Annealing Log
Record all errors encountered and their resolutions in the self-annealing log.

## Directive Log
Record all directives received and their status.

## Artifact Log
Record all artifacts created, modified, or deleted.
