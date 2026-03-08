import { _electron as electron, expect, test } from "@playwright/test";
import path from "node:path";

test("desktop shell boots to the home screen", async () => {
  const app = await electron.launch({
    args: [path.resolve(__dirname, "../../dist-electron/main.js")],
  });

  const window = await app.firstWindow();
  await expect(window.getByText("RegressionLab")).toBeVisible();
  await app.close();
});
