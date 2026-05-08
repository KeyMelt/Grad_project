from __future__ import annotations


def build_editor_shell_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>RL Workspace</title>
    <link
      rel="stylesheet"
      href="/static/vendor/xterm/css/xterm.css"
    />
    <link
      rel="stylesheet"
      href="/static/vendor/monaco-editor/min/vs/editor/editor.main.css"
    />
    <style>
      :root {
        color-scheme: dark;
        --bg: #0b1220;
        --panel: #111827;
        --panel-soft: #0f172a;
        --border: #1f2937;
        --text: #e5e7eb;
        --muted: #94a3b8;
        --accent: #3b82f6;
        --success: #22c55e;
        --danger: #ef4444;
      }

      * { box-sizing: border-box; }
      html, body { margin: 0; width: 100%; height: 100%; background: var(--bg); color: var(--text); font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif; }
      .shell {
        width: 100%;
        height: 100%;
        display: grid;
        grid-template-rows: 56px minmax(0, 1fr) 220px;
        gap: 10px;
        padding: 12px;
      }
      .toolbar, .terminal, .editor {
        border: 1px solid var(--border);
        border-radius: 14px;
        overflow: hidden;
        background: var(--panel);
      }
      .toolbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 14px;
        background: var(--panel-soft);
      }
      .toolbar .left,
      .toolbar .right {
        display: flex;
        align-items: center;
        gap: 10px;
      }
      .file-pill {
        padding: 7px 12px;
        border-radius: 999px;
        background: rgba(59, 130, 246, 0.12);
        color: #bfdbfe;
        font-weight: 700;
        font-size: 13px;
      }
      .status {
        font-size: 13px;
        color: var(--muted);
      }
      .button {
        border: 1px solid var(--border);
        background: #172033;
        color: var(--text);
        border-radius: 10px;
        padding: 8px 12px;
        cursor: pointer;
        font-weight: 600;
      }
      .button.primary {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        border-color: #1d4ed8;
      }
      .button:disabled {
        opacity: 0.55;
        cursor: default;
      }
      #editor {
        width: 100%;
        height: 100%;
      }
      .terminal {
        padding-top: 8px;
      }
      #terminal {
        width: 100%;
        height: 100%;
      }
    </style>
  </head>
  <body>
    <div class="shell">
      <div class="toolbar">
        <div class="left">
          <div class="file-pill">script.py</div>
          <div class="status" id="save-status">Loading workspace...</div>
        </div>
        <div class="right">
          <div class="status" id="console-status">Console: connecting</div>
          <button class="button primary" id="run-button">Run</button>
        </div>
      </div>
      <div class="editor">
        <div id="editor"></div>
      </div>
      <div class="terminal">
        <div id="terminal"></div>
      </div>
    </div>

    <script src="/static/vendor/xterm/lib/xterm.js"></script>
    <script src="/static/vendor/monaco-editor/min/vs/loader.js"></script>
    <script>
      const params = new URLSearchParams(window.location.search);
      const sessionId = params.get("session_id");
      const filePath = "script.py";
      const saveStatus = document.getElementById("save-status");
      const consoleStatus = document.getElementById("console-status");
      const runButton = document.getElementById("run-button");

      if (!sessionId) {
        document.body.innerHTML = "<div style='padding:24px;color:#fecaca'>Missing workspace session_id.</div>";
        throw new Error("Missing session_id");
      }

      const term = new Terminal({
        theme: {
          background: "#111827",
          foreground: "#E5E7EB",
          cursor: "#93C5FD",
        },
        fontFamily: "Menlo, Monaco, Consolas, monospace",
        fontSize: 13,
        convertEol: true,
      });
      term.open(document.getElementById("terminal"));

      let ws;
      let editor;
      let inputBuffer = "";
      let saveTimer = null;
      let currentVersion = 1;

      function writeTerm(text) {
        if (!text) return;
        term.write(text.replace(/\\n/g, "\\r\\n"));
      }

      function setSaveStatus(text, tone) {
        saveStatus.textContent = text;
        saveStatus.style.color = tone === "error" ? "#FCA5A5" : tone === "ok" ? "#86EFAC" : "#94A3B8";
      }

      function setConsoleStatus(text, tone) {
        consoleStatus.textContent = text;
        consoleStatus.style.color = tone === "error" ? "#FCA5A5" : tone === "ok" ? "#86EFAC" : "#94A3B8";
      }

      async function loadFile() {
        const response = await fetch(`/workspace/sessions/${sessionId}/files/${filePath}`);
        if (!response.ok) {
          throw new Error("Unable to load workspace file.");
        }
        const payload = await response.json();
        currentVersion = payload.version || 1;
        return payload;
      }

      async function saveFile(content) {
        const response = await fetch(`/workspace/sessions/${sessionId}/files/${filePath}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ content }),
        });
        if (!response.ok) {
          throw new Error("Unable to save workspace file.");
        }
        const payload = await response.json();
        currentVersion = payload.version || currentVersion;
        applyDiagnostics(payload.diagnostics || []);
        return payload;
      }

      function applyDiagnostics(diagnostics) {
        if (!editor || !window.monaco) return;
        const severityMap = {
          error: monaco.MarkerSeverity.Error,
          warning: monaco.MarkerSeverity.Warning,
          info: monaco.MarkerSeverity.Info,
          hint: monaco.MarkerSeverity.Hint,
        };
        const markers = diagnostics.map((item) => ({
          severity: severityMap[item.severity] || monaco.MarkerSeverity.Error,
          message: item.message,
          startLineNumber: item.line || 1,
          startColumn: item.column || 1,
          endLineNumber: item.line || 1,
          endColumn: (item.column || 1) + 1,
        }));
        monaco.editor.setModelMarkers(editor.getModel(), "workspace", markers);
      }

      function connectConsole() {
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        ws = new WebSocket(`${protocol}//${window.location.host}/workspace/sessions/${sessionId}/console`);
        ws.onopen = () => setConsoleStatus("Console: ready", "ok");
        ws.onclose = () => setConsoleStatus("Console: disconnected", "error");
        ws.onerror = () => setConsoleStatus("Console: failed", "error");
        ws.onmessage = (event) => {
          const payload = JSON.parse(event.data);
          switch (payload.type) {
            case "ready":
              setConsoleStatus("Console: ready", "ok");
              break;
            case "stdout":
              writeTerm(payload.data || "");
              break;
            case "stderr":
              writeTerm(payload.data || "");
              break;
            case "prompt":
              writeTerm(payload.prompt || ">>> ");
              inputBuffer = "";
              break;
            case "run_started":
              runButton.disabled = true;
              setConsoleStatus("Console: running script", null);
              break;
            case "run_finished":
              runButton.disabled = false;
              setConsoleStatus(`Console: run complete (exit ${payload.exit_code ?? 0})`, "ok");
              break;
            case "run_failed":
              runButton.disabled = false;
              setConsoleStatus(`Console: run failed (exit ${payload.exit_code ?? 1})`, "error");
              break;
            case "diagnostics":
              applyDiagnostics(payload.diagnostics || []);
              break;
          }
        };

        term.onData((data) => {
          if (!ws || ws.readyState !== WebSocket.OPEN) {
            return;
          }

          if (data === "\\r") {
            ws.send(JSON.stringify({ line: inputBuffer }));
            writeTerm("\\n");
            inputBuffer = "";
            return;
          }

          if (data === "\\u007F") {
            if (inputBuffer.length > 0) {
              inputBuffer = inputBuffer.slice(0, -1);
              term.write("\\b \\b");
            }
            return;
          }

          if (data >= " ") {
            inputBuffer += data;
            term.write(data);
          }
        });
      }

      function initMonaco(initialContent, diagnostics) {
        require.config({ paths: { vs: "/static/vendor/monaco-editor/min/vs" } });
        require(["vs/editor/editor.main"], function () {
          monaco.languages.registerCompletionItemProvider("python", {
            provideCompletionItems: function (model, position) {
              const words = Array.from(new Set(model.getValue().match(/[A-Za-z_][A-Za-z0-9_]*/g) || []));
              const suggestions = words.map((word) => ({
                label: word,
                kind: monaco.languages.CompletionItemKind.Variable,
                insertText: word,
              }));
              const keywords = ["def", "return", "for", "while", "if", "else", "import", "from", "class", "with", "try", "except"];
              for (const keyword of keywords) {
                suggestions.push({
                  label: keyword,
                  kind: monaco.languages.CompletionItemKind.Keyword,
                  insertText: keyword,
                });
              }
              return { suggestions };
            },
          });

          editor = monaco.editor.create(document.getElementById("editor"), {
            value: initialContent,
            language: "python",
            theme: "vs-dark",
            automaticLayout: true,
            minimap: { enabled: false },
            fontSize: 14,
            tabSize: 4,
            insertSpaces: true,
            wordBasedSuggestions: "allDocuments",
            quickSuggestions: true,
            scrollBeyondLastLine: false,
          });

          applyDiagnostics(diagnostics || []);

          editor.onDidChangeModelContent(() => {
            setSaveStatus("Saving...", null);
            if (saveTimer) {
              window.clearTimeout(saveTimer);
            }
            saveTimer = window.setTimeout(async () => {
              try {
                const payload = await saveFile(editor.getValue());
                setSaveStatus(`Saved v${payload.version}`, "ok");
              } catch (error) {
                setSaveStatus(error.message, "error");
              }
            }, 350);
          });
        });
      }

      runButton.addEventListener("click", async () => {
        runButton.disabled = true;
        try {
          const response = await fetch(`/workspace/sessions/${sessionId}/run`, { method: "POST" });
          if (!response.ok) {
            throw new Error("Unable to start run.");
          }
          const payload = await response.json();
          setConsoleStatus(`Console: run ${payload.run_id} started`, null);
        } catch (error) {
          setConsoleStatus(error.message, "error");
          runButton.disabled = false;
        }
      });

      (async () => {
        try {
          const file = await loadFile();
          initMonaco(file.content, file.diagnostics || []);
          connectConsole();
          setSaveStatus(`Loaded v${currentVersion}`, "ok");
        } catch (error) {
          setSaveStatus(error.message, "error");
        }
      })();
    </script>
  </body>
</html>
"""
