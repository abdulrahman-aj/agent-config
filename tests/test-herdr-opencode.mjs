import assert from "node:assert/strict";
import { once } from "node:events";
import { mkdtempSync, rmSync } from "node:fs";
import net from "node:net";
import os from "node:os";
import path from "node:path";
import { test } from "node:test";

import sessionSelection from "../opencode/herdr-tui-session.js";

async function herdrSocket(t) {
  const directory = mkdtempSync(path.join(os.tmpdir(), "herdr-opencode-"));
  const socketPath = path.join(directory, "socket");
  const previous = [process.env.HERDR_ENV, process.env.HERDR_PANE_ID, process.env.HERDR_SOCKET_PATH];
  Object.assign(process.env, {
    HERDR_ENV: "1",
    HERDR_PANE_ID: "pane-1",
    HERDR_SOCKET_PATH: socketPath,
  });

  const reports = [];
  const waiters = [];
  const server = net.createServer((client) => {
    let buffer = "";
    client.on("data", (chunk) => {
      buffer += chunk;
      if (!buffer.includes("\n")) return;
      reports.push(JSON.parse(buffer.slice(0, buffer.indexOf("\n"))));
      for (const notify of waiters.splice(0)) notify();
      client.end("ok\n");
    });
  });
  server.listen(socketPath);
  await once(server, "listening");

  t.after(async () => {
    server.close();
    await once(server, "close");
    ["HERDR_ENV", "HERDR_PANE_ID", "HERDR_SOCKET_PATH"].forEach((name, index) => {
      if (previous[index] === undefined) delete process.env[name];
      else process.env[name] = previous[index];
    });
    rmSync(directory, { recursive: true, force: true });
  });

  async function waitFor(count, timeout = 2_000) {
    while (reports.length < count) {
      let timer;
      try {
        await Promise.race([
          new Promise((resolve) => waiters.push(resolve)),
          new Promise((_, reject) => {
            timer = setTimeout(() => reject(new Error("Herdr report timed out")), timeout);
          }),
        ]);
      } finally {
        clearTimeout(timer);
      }
    }
    return reports;
  }

  return { waitFor };
}

test("V2 TUI reports its selected session without attributing child work to it", async (t) => {
  const socket = await herdrSocket(t);
  const route = { type: "session", sessionID: "root" };
  let onEvent;
  const dispose = sessionSelection.setup({
    ui: { router: { current: () => route } },
    data: {
      listen: (callback) => { onEvent = callback; return () => {}; },
      session: {
        get: (id) => id === "child" ? { id, parentID: "root" } : { id },
        root: (id) => id === "child" ? "root" : id,
      },
    },
  });
  t.after(dispose);

  await socket.waitFor(1);
  route.sessionID = "child";
  await new Promise((resolve) => setTimeout(resolve, 125));
  for (const [type, data] of [
    ["session.execution.started", { sessionID: "root" }],
    ["permission.asked", { sessionID: "child" }],
    ["permission.replied", { sessionID: "child" }],
    ["session.execution.started", { sessionID: "other" }],
    ["session.idle", { sessionID: "root" }],
    ["session.status", { sessionID: "root", status: { type: "idle" } }],
  ]) onEvent({ details: { type, data } });

  const reports = await socket.waitFor(6);
  assert.deepEqual(reports.slice(1).map(({ params }) => [params.state, params.agent_session_id]), [
    ["working", "root"],
    ["blocked", undefined],
    ["working", undefined],
    ["idle", "root"],
    ["idle", "root"],
  ]);
  assert.ok(reports.slice(1).every(({ method, params }) => method === "pane.report_agent" &&
    params.pane_id === "pane-1"));
});

test("V2 TUI selection reports the selected root session", async (t) => {
  const socket = await herdrSocket(t);
  const dispose = sessionSelection.setup({
    ui: { router: { current: () => ({ type: "session", sessionID: "root" }) } },
    data: { listen: () => () => {}, session: { get: () => ({ id: "root" }) } },
  });
  t.after(dispose);

  const [report] = await socket.waitFor(1);
  assert.equal(report.method, "pane.report_agent_session");
  assert.equal(report.params.agent_session_id, "root");
  assert.equal(report.params.session_start_source, "select");
});

test("V2 TUI re-announces the selected session after the initial retry window", async (t) => {
  const socket = await herdrSocket(t);
  const dispose = sessionSelection.setup({
    ui: { router: { current: () => ({ type: "session", sessionID: "root" }) } },
    data: { listen: () => () => {}, session: { get: () => ({ id: "root" }) } },
  });
  t.after(dispose);

  const reports = await socket.waitFor(5, 8_000);
  assert.ok(reports.every((report) => report.method === "pane.report_agent_session" &&
    report.params.agent_session_id === "root"));
});
