import "./webllm.css";
import "./uuid.js";
import html from "./webllm.html";
import { generateUUID } from "./uuid.js";

//https://github.com/Vaibhavs10/github-issue-generator-webgpu/
import { prebuiltAppConfig, CreateMLCEngine } from "@mlc-ai/web-llm";

function render({ model, el }) {
  let engine = null;
  let useCustomGrammar = false;

  const _headless = model.get("headless");

  let el2 = document.createElement("div");
  el2.innerHTML = html;
  const uuid = generateUUID();
  el2.id = uuid;

  // For the headless version,
  // just suppress the visible display of the widget UI
  if (_headless) {
    el2.style = "display: none; visibility: hidden;";
  }

  el.appendChild(el2);

  const modelSelection = el.querySelector(".webllm-model-select");
  const promptTextarea = el.querySelector('textarea[name="webllm-prompt"]');
  const outputDiv = el.querySelector('div[title="webllm-output"]');

  const availableModels = prebuiltAppConfig.model_list
    .filter((m) => m.model_id.startsWith("SmolLM2"))
    .map((m) => m.model_id);

  let selectedModel = availableModels[0];

  availableModels.forEach((modelId) => {
    const option = document.createElement("option");
    option.value = modelId;
    option.textContent = modelId;
    modelSelection.appendChild(option);
  });

  outputDiv.innerHTML = "<div>waiting</div>";
  if (!engine) {
    outputDiv.innerHTML = "<div>getting ready</div>";
    CreateMLCEngine(selectedModel, {
      initProgressCallback: (progress) => {
        console.log(progress);
        outputDiv.innerHTML = `<div class="loading">${progress.text}</div>`;
      },
    }).then((createdEngine) => {
      engine = createdEngine;
      model.set("about", {
        widget: "jupyter_anywidget_webllm",
        webllm_model: selectedModel,
      });
      model.set("response", { status: "ready" });
      model.save_changes();
    });

    model.on("change:doc_content", () => {
      const input_raw = model.get("doc_content");
      if (input_raw == "") {
        model.set("response", {
          status: "aborted",
        });
        model.save_changes();
        return;
      }
      let valid_template = true;
      const output_template = model.get("output_template");
      let response_format = {};
      if (output_template) {
        try {
          const schema = JSON.stringify(JSON.parse(output_template));
          response_format = { type: "json_object", schema };
        } catch {
          alert("Template does not validate");
          model.set("response", {
            status: "aborted",
          });
          model.save_changes();
          return;
        }
      }

      const temperature = model.get("temperature");
      const request = {
        stream: true,
        stream_options: { include_usage: false },
        messages: [{ role: "user", content: input_raw }],
        max_tokens: model.get("params").max_tokens ?? 512,
        response_format,
        temperature: model.get("params").temperature ?? 0.5,
        top_p: model.get("params").top_p ?? 0.5,
        frequency_penalty: model.get("params").frequency_penalty ?? 0.5,
        presence_penalty: model.get("params").presence_penalty ?? 0.3,
      };
      model.set("response", {
        status: "working on it...",
        output_template: output_template,
        input_raw: input_raw,
      });
      model.save_changes();
      promptTextarea.innerHTML = input_raw;

      function process_chat(model, engine) {
        return engine.chatCompletion(request).then((generator) => {
          let curMessage = "";
          let usage = null;

          return new Promise((resolve, reject) => {
            const processChunks = () => {
              generator
                .next()
                .then((result) => {
                  if (result.done) {
                    return engine.getMessage().then((finalMessage) => {
                      model.set("output_raw", finalMessage);
                      model.set("response", {
                        status: "completed",
                        output_raw: finalMessage,
                        max_tokens: model.get("params").max_tokens ?? 512,
                        temperature: model.get("params").temperature ?? 0.5,
                        top_p: model.get("params").top_p ?? 0.5,
                        frequency_penalty:
                          model.get("params").frequency_penalty ?? 0.5,
                        presence_penalty:
                          model.get("params").presence_penalty ?? 0.3,
                      });
                      model.save_changes();
                      resolve(finalMessage);
                    });
                  }

                  const chunk = result.value;
                  const curDelta = chunk.choices[0]?.delta.content;
                  if (curDelta) curMessage += curDelta;

                  if (chunk.usage) {
                    console.log(chunk.usage);
                    usage = chunk.usage;
                  }

                  outputDiv.innerHTML = `<pre><code class="language-json">${curMessage}</code></pre>`;

                  return processChunks();
                })
                .catch(reject);
            };

            processChunks();
          });
        });
      }

      process_chat(model, engine).then((finalMessage) => {
        // Post-processing logic
        outputDiv.innerHTML = finalMessage;
        try {
          //const issueData = JSON.parse(finalMessage);
          //updateIssuePreview(issueData);
        } catch (error) {
          console.error("Failed to parse issue data:", error);
        }
      });
    });
  }
  outputDiv.innerHTML = "<div>done</div>";
}

export default { render };
