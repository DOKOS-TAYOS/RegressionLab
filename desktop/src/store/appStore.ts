import { create } from "zustand";

import { desktopClient } from "@/api/client";
import type { BootstrapPayload, HelpPayload } from "@/types";

type Banner = {
  tone: "info" | "error" | "success";
  messageKey: string;
  params?: Record<string, unknown>;
  details?: unknown;
};

type AppStore = {
  loading: boolean;
  bootstrap: BootstrapPayload | null;
  help: HelpPayload | null;
  banner: Banner | null;
  activeLanguage: string;
  initialize: () => Promise<void>;
  loadHelp: () => Promise<void>;
  setBanner: (banner: Banner | null) => void;
  setLanguage: (language: string) => void;
};

export const useAppStore = create<AppStore>((set, get) => ({
  loading: true,
  bootstrap: null,
  help: null,
  banner: null,
  activeLanguage: "es",
  initialize: async () => {
    set({ loading: true });
    try {
      const bootstrap = await desktopClient.getBootstrap();
      set({
        bootstrap,
        activeLanguage: bootstrap.activeLanguage,
        loading: false,
      });
    } catch (error) {
      const payload = error as { error?: { messageKey?: string; details?: unknown } };
      set({
        loading: false,
        banner: {
          tone: "error",
          messageKey: payload.error?.messageKey ?? "desktop.error.internal",
          details: payload.error?.details,
        },
      });
    }
  },
  loadHelp: async () => {
    if (get().help) {
      return;
    }
    try {
      const help = await desktopClient.getHelp();
      set({ help });
    } catch (error) {
      const payload = error as { error?: { messageKey?: string; details?: unknown } };
      set({
        banner: {
          tone: "error",
          messageKey: payload.error?.messageKey ?? "desktop.error.internal",
          details: payload.error?.details,
        },
      });
    }
  },
  setBanner: (banner) => set({ banner }),
  setLanguage: (language) => set({ activeLanguage: language }),
}));
