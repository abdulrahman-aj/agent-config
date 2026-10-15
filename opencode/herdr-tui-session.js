import { createReporter } from "./herdr-report.js";

export default {
  id: "herdr.opencode.session-selection",
  setup(context) {
    const reporter = createReporter();
    if (!reporter) return;

    let selectedID;
    let retry = 0;
    let nextReportAt = 0;
    let pending = false;
    const retryDelays = [100, 400, 1_000, 5_000];

    // The shared V2 server may start outside Herdr, so report from the pane's TUI.
    const stop = context.data.listen(({ details: event }) => {
      const { type, data } = event;
      const sessionID = data?.sessionID ?? data?.form?.sessionID;
      if (!selectedID || !sessionID) return;
      const belongsToSelection = sessionID === selectedID ||
        data?.parentID === selectedID || context.data.session.root(sessionID) === selectedID;
      if (!belongsToSelection) return;

      const child = sessionID !== selectedID;
      let state;
      if (type === "permission.asked" || type === "form.created") {
        state = "blocked";
      } else if (type === "permission.replied" || type === "form.replied" || type === "form.cancelled") {
        state = "working";
      } else if (!child) {
        if (type === "session.status") {
          state = data.status.type === "idle" ? "idle" : "working";
        } else if (type === "session.idle" ||
          type === "session.execution.succeeded" || type === "session.execution.interrupted") {
          state = "idle";
        } else if (type === "session.execution.failed") {
          state = "blocked";
        } else if (type === "session.execution.started" || type === "session.compaction.ended") {
          state = "working";
        }
      }
      if (state) void reporter.state(state, child ? undefined : sessionID);
    });

    async function sync() {
      const route = context.ui.router.current();
      const sessionID = route?.type === "session" ? route.sessionID : undefined;
      const session = sessionID ? context.data.session.get(sessionID) : undefined;
      if (session?.parentID) return;
      if (!session) {
        selectedID = undefined;
        retry = 0;
        nextReportAt = 0;
        return;
      }

      if (sessionID !== selectedID) {
        selectedID = sessionID;
        retry = 0;
        nextReportAt = 0;
      }
      if (pending || Date.now() < nextReportAt) return;

      pending = true;
      try {
        await reporter.selection(sessionID);
      } finally {
        pending = false;
      }
      if (selectedID !== sessionID) return;
      // Keep re-announcing at a slower rate if Herdr restarts during this TUI session.
      nextReportAt = Date.now() + retryDelays[Math.min(retry, retryDelays.length - 1)];
      retry++;
    }

    void sync();
    const timer = setInterval(() => void sync(), 100);
    return () => {
      clearInterval(timer);
      stop();
    };
  },
};
