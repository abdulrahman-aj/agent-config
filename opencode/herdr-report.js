import net from "node:net";

const SOURCE = "herdr:opencode";

export function createReporter() {
  const paneID = process.env.HERDR_PANE_ID;
  const socketPath = process.env.HERDR_SOCKET_PATH;
  if (process.env.HERDR_ENV !== "1" || !paneID || !socketPath) return;

  const endpoint = process.platform === "win32" ? `\\\\.\\pipe\\${socketPath}` : socketPath;
  let sequence = Date.now() * 1000;
  let pending = Promise.resolve();

  function send(method, params) {
    const message = {
      id: `${SOURCE}:${Date.now()}:${Math.floor(Math.random() * 1_000_000)}`,
      method,
      params: { pane_id: paneID, source: SOURCE, agent: "opencode", seq: ++sequence, ...params },
    };

    const next = pending.then(() => new Promise((resolve) => {
      const socket = net.createConnection(endpoint, () => socket.write(`${JSON.stringify(message)}\n`));
      const finish = () => {
        socket.destroy();
        resolve();
      };
      socket.setTimeout(500, finish);
      socket.on("data", finish);
      socket.on("error", finish);
      socket.on("end", finish);
      socket.on("close", resolve);
    }));
    pending = next.catch(() => {});
    return next;
  }

  return {
    state(state, sessionID) {
      return send("pane.report_agent", {
        state,
        ...(sessionID ? { agent_session_id: sessionID } : {}),
      });
    },
    selection(sessionID) {
      return send("pane.report_agent_session", {
        agent_session_id: sessionID,
        session_start_source: "select",
      });
    },
  };
}
