# Vertex AI Agent Builder assets

Use these files to wire the Clinical Record Companion agent inside Vertex AI Agent Builder (Agentspace).

## How to import

1. Create a new agent or open the existing Gemini Enterprise agent.
2. Add the `parse_ccda` and `reconcile_records` tools manually:
   - Choose **Cloud Function / HTTP** or **Webhook** tool types.
   - Paste the JSON Schema definitions from `tools.json` into the parameter/response schema editors.
   - Point the HTTPS endpoints to the deployed Cloud Function and Cloud Run URLs from `infra/deploy.sh` output.
3. Paste the content of `system_prompt.txt` into the agent system instructions.
4. Add evaluation prompts such as:
   - "Parse the two most recent CCDAs from the raw bucket and reconcile medication differences."
   - "Do any medications conflict with allergies? Cite the facility and date."

## Future enhancement

- TODO: integrate Vertex AI Search datastore `patient-data_1762901262843` once permissions land. It can enrich responses with longitudinal labs and care plans beyond the medication scope handled today.
